from itertools import product

import numpy as np


def cluster_blocks(
    coords: np.ndarray,
    distance: int = 1,
) -> list[tuple[float, float, float]]:
    """Group nearby portal blocks and average each group into one location.

    Two blocks belong to the same portal when they are within ``distance``
    blocks of each other on every axis (Chebyshev distance). Since a portal's
    interior blocks are face-contiguous, this collapses every portal into a
    single averaged ``(x, y, z)`` point.

    Args:
        coords: An ``(N, 3)`` int array of portal block world coordinates.
        distance: Maximum per-axis gap for two blocks to be connected.

    Returns:
        A list of averaged ``(x, y, z)`` portal centers.
    """
    if len(coords) == 0:
        return []

    coord_tuples = [(int(x), int(y), int(z)) for x, y, z in coords]
    index_of = {coord: i for i, coord in enumerate(coord_tuples)}
    parent = list(range(len(coord_tuples)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        root_a, root_b = find(a), find(b)
        if root_a != root_b:
            parent[root_b] = root_a

    offsets = [
        offset
        for offset in product(range(-distance, distance + 1), repeat=3)
        if offset != (0, 0, 0)
    ]

    for coord, i in index_of.items():
        cx, cy, cz = coord
        for dx, dy, dz in offsets:
            neighbor = index_of.get((cx + dx, cy + dy, cz + dz))
            if neighbor is not None:
                union(i, neighbor)

    groups: dict[int, list[int]] = {}
    for i in range(len(coord_tuples)):
        groups.setdefault(find(i), []).append(i)

    centers: list[tuple[float, float, float]] = []
    for members in groups.values():
        mean = coords[members].mean(axis=0)
        centers.append((float(mean[0]), float(mean[1]), float(mean[2])))
    return centers
