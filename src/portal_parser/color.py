import colorsys
from random import Random


def random_hue_color(
    rng: Random,
    saturation: float = 0.44,
    value: float = 0.95,
) -> str:
    """Generate a hex color with a random hue but fixed saturation/value.

    Args:
        rng: Random generator used to pick the hue (for reproducibility).
        saturation: HSV saturation, kept constant across colors.
        value: HSV value/brightness, kept constant across colors.

    Returns:
        A ``'#rrggbb'`` color string.
    """
    red, green, blue = colorsys.hsv_to_rgb(rng.random(), saturation, value)
    return '#{:02x}{:02x}{:02x}'.format(
        round(red * 255),
        round(green * 255),
        round(blue * 255),
    )
