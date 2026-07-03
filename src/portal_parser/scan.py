from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import anvil
import numpy as np
from anvil.errors import ChunkNotFound, GZipChunkData
from nbt import nbt

PORTAL_BLOCK_ID = 90
"""Numeric block ID of the nether portal block (pre-flattening, pre-1.13)."""

PORTAL_BLOCK_NAMES = frozenset({'nether_portal', 'portal'})
"""Flattened (1.13+) block IDs of the nether portal, without the namespace."""

_DIMENSION_DIRS: dict[str, tuple[str, ...]] = {
    'ow': ('region',),
    'nether': ('DIM-1', 'region'),
    'end': ('DIM1', 'region'),
}
"""Maps a dimension name to its region sub-folder inside a world directory."""


def _region_dir(world_dir: Path, dimension: str) -> Path:
    """Resolve the region folder for a dimension inside a world directory.

    Args:
        world_dir: Path to the world save (the folder holding ``level.dat``).
        dimension: One of ``'ow'``, ``'nether'`` or ``'end'``.

    Returns:
        Path to the dimension's ``region`` folder.

    Raises:
        ValueError: If ``dimension`` is not a recognised value.
    """
    try:
        parts = _DIMENSION_DIRS[dimension]
    except KeyError as exc:
        valid = ', '.join(sorted(_DIMENSION_DIRS))
        raise ValueError(
            f'Unknown dimension {dimension!r}; expected one of: {valid}'
        ) from exc
    return world_dir.joinpath(*parts)


def _sections(chunk: anvil.Chunk) -> list:
    """Return the raw section list of a chunk, handling every layout.

    Older chunks store sections under ``Sections`` (inside ``Level``); 1.18+
    chunks use ``sections`` at the chunk root. Both are exposed via
    ``chunk.data`` by anvil-parser2.
    """
    for key in ('Sections', 'sections'):
        if key in chunk.data:
            return chunk.data[key]
    return []


def _legacy_portal_indices(section: nbt.TAG_Compound) -> np.ndarray:
    """Find portal block indices in a pre-1.13 (numeric ``Blocks``) section.

    Args:
        section: A section compound containing a ``Blocks`` byte array.

    Returns:
        A 1-D array of block indices (0-4095) that are portal blocks.
    """
    blocks = np.frombuffer(section['Blocks'].value, dtype=np.uint8)
    idxs = np.nonzero(blocks == PORTAL_BLOCK_ID)[0]
    # The optional `Add` nibble array carries the high bits of block IDs > 255.
    # A block whose low byte is 90 but has a non-zero Add nibble is NOT a portal.
    if idxs.size and 'Add' in section:
        add = np.frombuffer(section['Add'].value, dtype=np.uint8)
        packed = add[idxs // 2]
        high = idxs % 2 == 1
        nibbles = np.where(high, packed >> 4, packed & 0x0F)
        idxs = idxs[nibbles == 0]
    return idxs


def _flattened_portal_indices(
    chunk: anvil.Chunk,
    section: nbt.TAG_Compound,
) -> np.ndarray:
    """Find portal block indices in a flattened (1.13+, palette) section.

    The section's palette is checked first as a cheap rejection test; the block
    states are only decoded for sections that actually contain a portal block.

    Args:
        chunk: The owning chunk (used for palette/state decoding).
        section: A palette-based section compound.

    Returns:
        A 1-D array of block indices (0-4095) that are portal blocks.
    """
    try:
        palette = chunk.get_palette(section)
    except KeyError:
        return np.empty(0, dtype=np.int64)
    if not palette or not any(block.id in PORTAL_BLOCK_NAMES for block in palette):
        return np.empty(0, dtype=np.int64)

    indices = [
        index
        for index, block in enumerate(chunk.stream_blocks(section=section))
        if block.id in PORTAL_BLOCK_NAMES
    ]
    return np.asarray(indices, dtype=np.int64)


def _scan_region_file(region_path: str) -> np.ndarray:
    """Scan a single region file for portal blocks.

    This is the unit of work distributed across processes, so it must be a
    top-level, picklable function that takes a plain path string.

    Args:
        region_path: Filesystem path to a ``r.*.mca`` region file.

    Returns:
        An ``(N, 3)`` int array of world ``(x, y, z)`` portal-block coordinates.
    """
    region = anvil.Region.from_file(region_path)
    chunks: list[np.ndarray] = []

    for local_x in range(32):
        for local_z in range(32):
            try:
                chunk = region.get_chunk(local_x, local_z)
            except (ChunkNotFound, GZipChunkData):
                # Chunk not generated yet, or uses unsupported gzip framing.
                continue

            base_x = chunk.x * 16
            base_z = chunk.z * 16
            for section in _sections(chunk):
                if 'Blocks' in section:
                    idxs = _legacy_portal_indices(section)
                else:
                    idxs = _flattened_portal_indices(chunk, section)
                if not idxs.size:
                    continue

                section_y = section['Y'].value
                local_y = idxs // 256
                remainder = idxs % 256
                local_z_in = remainder // 16
                local_x_in = remainder % 16

                xs = base_x + local_x_in
                ys = section_y * 16 + local_y
                zs = base_z + local_z_in
                chunks.append(np.stack([xs, ys, zs], axis=1))

    if not chunks:
        return np.empty((0, 3), dtype=np.int64)
    return np.concatenate(chunks).astype(np.int64)


def find_portal_blocks(
    world_dir: str | Path,
    dimension: str = 'ow',
    workers: int | None = None,
) -> np.ndarray:
    """Find every nether-portal block in a dimension of a world.

    Region files are scanned in parallel across processes, which sidesteps the
    GIL for the CPU-bound chunk decompression and NBT parsing.

    Works across Minecraft versions: pre-1.13 chunks are scanned by numeric
    block ID, while 1.13+ chunks (including 1.18+ layouts) are scanned by the
    flattened block name.

    Args:
        world_dir: Path to the world save (the folder holding ``level.dat``).
        dimension: Dimension to scan; one of ``'ow'``, ``'nether'`` or ``'end'``.
        workers: Number of worker processes. ``None`` uses all CPU cores; ``1``
            runs sequentially in-process (useful for debugging).

    Returns:
        An ``(N, 3)`` int array of world ``(x, y, z)`` coordinates, one row per
        portal block. Empty ``(0, 3)`` array if none are found.
    """
    region_dir = _region_dir(Path(world_dir), dimension)
    region_paths = [str(path) for path in sorted(region_dir.glob('r.*.mca'))]
    if not region_paths:
        return np.empty((0, 3), dtype=np.int64)

    if workers == 1:
        results = [_scan_region_file(path) for path in region_paths]
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(_scan_region_file, region_paths))

    non_empty = [result for result in results if result.size]
    if not non_empty:
        return np.empty((0, 3), dtype=np.int64)
    return np.concatenate(non_empty)
