from pathlib import Path
from random import Random

from .cluster import cluster_blocks
from .color import random_hue_color
from .export import PortalLocation, save_portals
from .scan import find_portal_blocks

__all__ = [
    'PortalLocation',
    'find_portal_locations',
    'save_portals',
]


def find_portal_locations(
    world_dir: str | Path,
    dimension: str = 'ow',
    coordinate_multiplier: float = 1 / 8,
    cluster_distance: int = 1,
    saturation: float = 0.44,
    value: float = 0.95,
    seed: int | None = None,
    workers: int | None = None,
) -> list[PortalLocation]:
    """Find and label every portal location in a world dimension.

    Scans the chosen dimension for nether-portal blocks, groups connected
    blocks into single portals, averages each group and applies
    ``coordinate_multiplier`` to the horizontal axes (X and Z only). Portals are
    ordered by Chebyshev distance from the origin, ``max(|x|, |z|)``, and each is
    assigned a sequential name (0 = closest to origin) and a random-hue color.

    Args:
        world_dir: Path to the world save (the folder holding ``level.dat``).
        dimension: Dimension to scan; ``'ow'``, ``'nether'`` or ``'end'``.
        coordinate_multiplier: Factor applied to X and Z (e.g. ``1/8`` to
            convert Overworld coordinates to Nether scale). Y is never scaled.
        cluster_distance: Maximum per-axis gap for blocks of the same portal.
        saturation: Constant HSV saturation for portal colors.
        value: Constant HSV value/brightness for portal colors.
        seed: Optional seed for reproducible colors.
        workers: Number of worker processes for scanning. ``None`` uses all CPU
            cores; ``1`` runs sequentially.

    Returns:
        A list of :class:`PortalLocation`, ordered by Chebyshev distance from
        the origin.
    """
    blocks = find_portal_blocks(world_dir, dimension, workers=workers)
    centers = cluster_blocks(blocks, distance=cluster_distance)

    coords = [
        (
            round(center_x * coordinate_multiplier),
            round(center_z * coordinate_multiplier),
            round(center_y),
        )
        for center_x, center_y, center_z in centers
    ]
    # Order by Chebyshev distance to (0, 0) in the X/Z plane, closest first.
    coords.sort(key=lambda c: (max(abs(c[0]), abs(c[1])), c[0], c[1], c[2]))

    rng = Random(seed)
    return [
        PortalLocation(
            name=str(index),
            description='',
            color=random_hue_color(rng, saturation, value),
            x=x,
            z=z,
            y=y,
        )
        for index, (x, z, y) in enumerate(coords)
    ]
