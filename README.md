<div align="center">
  <img src="assets/portal-location-parser-logo.webp" alt="portal-location-parser logo" style="width:96px; image-rendering: pixelated;" onerror="this.style.display='none';">
  <h1>portal-location-parser</h1>
  <h3>Python tool for finding nether portal locations in a given world save file</h3>
  <p><i>Minecraft Java Edition 1.2.1 - 26.2</i></p>
</div>

> [!NOTE]
> This is a companion tool for the solver of [bolt routing problem web-app](https://github.com/KK-mp4/Bolt-Routing-Problem-V2)

<!-- DeepWiki badge here: https://deepwiki.ryoppippi.com/ -->

## Introduction

To generate a piston bolt network you first need to map all the stations in your world. For old SMP server this might be quite a big task, so this small helper tool exists:

- scans **Overworld**, **Nether**, and **End** dimensions
- supports Minecraft saves from **1.2.1** (Anvil `.mca` format) through current releases
- clusters adjacent portal blocks into one location per portal
- applies an optional X/Z coordinate multiplier (default `1/8` for Overworld → Nether scale)
- parallel region scanning across CPU cores

## Minecraft version support

| Era | Support |
|-|-|
| **1.2.1 – 1.12** | Numeric block ID `90` in legacy chunk sections |
| **1.13 – 1.17** | Flattened block names (`nether_portal`, `portal`) |
| **1.18+** | Same block names; updated chunk section layout |

**Not supported:** pre-Anvil saves that use McRegion `.mcr` files instead of `.mca` region files.

Chunk parsing is delegated to [anvil-parser2](https://pypi.org/project/anvil-parser2/). Some chunks with unsupported gzip framing are skipped silently.

## Setup with [Python](https://www.python.org/downloads/)

```bash
# Install the UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
# powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" on Windows

# Clone the repository and navigate into it
git clone https://github.com/KK-mp4/portal-location-parser.git
cd portal-location-parser

# Create virtual environment and install dependencies
uv sync
```

## Usage

### Command line

Point the tool at a world directory (the folder that contains `level.dat`):

```bash
uv run python -m main path/to/world
```

Common options:

```bash
# Scan the Nether and write to a custom path
uv run python -m main path/to/world -d nether -o output/nether-portals.json

# Keep raw Overworld coordinates (no 1/8 scaling)
uv run python -m main path/to/world -m 1

# Limit worker processes (default: all CPU cores)
uv run python -m main path/to/world -w 4
```

| Flag | Default | Description |
|-|-|-|
| `-o`, `--output` | `output/<world-name>-portals.json` | Output JSON path (world name is lowercased; non-alphanumeric characters become `-`) |
| `-d`, `--dimension` | `ow` | Dimension to scan: `ow`, `nether`, or `end` |
| `-m`, `--coordinate-multiplier` | `0.125` (`1/8`) | Multiplier applied to X and Z only |
| `--cluster-distance` | `1` | Max per-axis gap between blocks of the same portal |
| `--seed` | none | Seed for reproducible portal colors |
| `-w`, `--workers` | all cores | Number of parallel worker processes |

### Python API

```python
from portal_parser import find_portal_locations, save_portals

portals = find_portal_locations(
    'path/to/world',
    dimension='ow',
    coordinate_multiplier=1 / 8,
)

save_portals(portals, 'output/portals.json')
```

See [`notebooks/example.ipynb`](notebooks/example.ipynb) for a full walkthrough that scans a sample world and plots the results with matplotlib.

## Development

```bash
# Activate virtual environment
. .venv/bin/activate
# .venv\Scripts\activate on Windows

# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit
uv run pre-commit run --all-files

# Format and lint
uv run ruff format
uv run ruff check --fix

# Type check
uv run pyright
```

## Contributors

<a href="https://github.com/KK-mp4/portal-location-parser/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=KK-mp4/portal-location-parser" alt="GitHub contributors" />
</a>

## [License](https://github.com/KK-mp4/portal-location-parser/blob/master/LICENSE.md)

This program is licensed under the MIT License. Please read the License file to know about the usage terms and conditions.
