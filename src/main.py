import argparse
import re
from pathlib import Path

from portal_parser import find_portal_locations, save_portals


def default_output_path(world_dir: str | Path) -> Path:
    """Build ``output/<world-slug>-portals.json`` from a world directory name."""
    world_name = Path(world_dir).name
    slug = re.sub(r'[^a-zA-Z0-9]', '-', world_name).lower()
    return Path('output') / f'{slug}-portals.json'


def main() -> None:
    """Parse CLI arguments, find portal locations and write them to JSON."""
    parser = argparse.ArgumentParser(
        description='Find nether-portal locations in a Minecraft save.',
    )
    parser.add_argument('world_dir', help='Path to the world save folder.')
    parser.add_argument(
        '-o',
        '--output',
        default=None,
        help='Output JSON path (default: output/<world-name>-portals.json).',
    )
    parser.add_argument(
        '-d',
        '--dimension',
        default='ow',
        choices=['ow', 'nether', 'end'],
        help='Dimension to scan.',
    )
    parser.add_argument(
        '-m',
        '--coordinate-multiplier',
        type=float,
        default=1 / 8,
        help='Factor applied to X and Z (not Y).',
    )
    parser.add_argument(
        '--cluster-distance',
        type=int,
        default=1,
        help='Max per-axis gap for blocks of the same portal.',
    )
    parser.add_argument('--seed', type=int, default=None, help='Color seed.')
    parser.add_argument(
        '-w',
        '--workers',
        type=int,
        default=None,
        help='Worker processes for scanning (default: all cores).',
    )
    args = parser.parse_args()
    output_path = args.output or default_output_path(args.world_dir)

    portals = find_portal_locations(
        args.world_dir,
        dimension=args.dimension,
        coordinate_multiplier=args.coordinate_multiplier,
        cluster_distance=args.cluster_distance,
        seed=args.seed,
        workers=args.workers,
    )
    save_portals(portals, output_path)
    print(f'Found {len(portals)} portal(s); wrote {output_path}')


if __name__ == '__main__':
    main()
