import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class PortalLocation:
    """A single portal location in the ``portals.json`` station schema.

    Attributes:
        name: Station name (a sequential index as a string).
        description: Free-form description (empty by default).
        color: Hex color string, e.g. ``'#f2a788'``.
        x: Horizontal X coordinate (after any coordinate multiplier).
        z: Horizontal Z coordinate (after any coordinate multiplier).
        y: Vertical coordinate (never scaled).
    """

    name: str
    description: str
    color: str
    x: int
    z: int
    y: int


def save_portals(portals: Iterable[PortalLocation], path: str | Path) -> None:
    """Write portal locations to a ``portals.json`` file.

    Args:
        portals: The portal locations to serialize.
        path: Destination file path; parent folders are created as needed.
    """
    data = {
        'stations': [asdict(portal) for portal in portals],
        'bolts': [],
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
        file.write('\n')
