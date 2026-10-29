"""Generate synthetic grayscale images with circular objects."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite
from numbers import Real

import numpy as np
from numpy.typing import NDArray

from validation import validate_integer


@dataclass(frozen=True)
class Circle:
    """Geometry in pixels and integer intensity (0–255).

    Coordinates start at the top left, x increasing right and y increasing down.
    Centers may lie outside the image. Zero radius selects an exact pixel center.
    """

    center_x: float
    center_y: float
    radius: float
    intensity: int


def generate_image(
    width: int,
    height: int,
    circles: Sequence[Circle],
    *,
    background: int = 200,
) -> NDArray[np.uint8]:
    """Return a fresh writable uint8 array, shape (height, width), indexed [y, x].

    Boundaries are included; image edges clip circles. Later circles overwrite
    overlaps. Inputs are unchanged and the caller owns the returned array.
    Generation performs no file I/O. Invalid types raise TypeError; invalid
    values raise ValueError. Geometry is computed in float64 pixel coordinates.
    """
    validate_integer(width, "width", 1)
    validate_integer(height, "height", 1)
    validate_integer(background, "background", 0, 255)
    if not isinstance(circles, Sequence):
        raise TypeError("circles must be a sequence of Circle objects")
    for index, circle in enumerate(circles):
        _validate_circle(circle, index)

    image = np.full((height, width), background, dtype=np.uint8)
    y, x = np.ogrid[:height, :width]
    for circle in circles:
        # Hypot avoids overflow from squaring large coordinates or radii.
        distance = np.hypot(x - float(circle.center_x), y - float(circle.center_y))
        image[distance <= circle.radius] = circle.intensity
    return image


def _validate_circle(circle: Circle, index: int) -> None:
    if not isinstance(circle, Circle):
        raise TypeError(f"circles[{index}] must be a Circle")
    for name in ("center_x", "center_y", "radius"):
        value = getattr(circle, name)
        if isinstance(value, bool) or not isinstance(value, Real):
            raise TypeError(f"circles[{index}].{name} must be a real number")
        try:
            finite = isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError(f"circles[{index}].{name} must be finite in float64")
    if circle.radius < 0:
        raise ValueError(f"circles[{index}].radius must be nonnegative")
    validate_integer(circle.intensity, f"circles[{index}].intensity", 0, 255)


def main() -> None:
    """Save a two-circle example to synthetic.png and report its array format."""
    from PIL import Image

    image = generate_image(
        256, 256, [Circle(0, 200, 20, 45), Circle(160, 100, 30, 90)]
    )
    Image.fromarray(image).save("synthetic.png")
    print(f"Shape: {image.shape}")
    print(f"Data type: {image.dtype}")


if __name__ == "__main__":
    main()
