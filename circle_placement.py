"""Seeded rejection sampling of visible, non-overlapping circles."""

from dataclasses import dataclass
from math import hypot, isfinite
from numbers import Real

import numpy as np

from synthetic_image import Circle
from validation import validate_integer


@dataclass(frozen=True)
class CirclePlacementResult:
    """Accepted circles and global proposal count; partial results are valid.

    The accepted count is len(circles); completion means it equals requested_count.
    """

    circles: tuple[Circle, ...]
    requested_count: int
    attempts: int


def generate_circles(
    width: int,
    height: int,
    count: int,
    radius: float,
    intensity: int,
    seed: int,
    max_attempts: int,
) -> CirclePlacementResult:
    """Sample visible circles using one global rejection-sampling budget.

    Pixel coordinates use a top-left origin. The continuous visible rectangle is
    [0, width - 1] × [0, height - 1]. Centers are sampled uniformly from that
    rectangle extended by radius on every side. Circle/rectangle tangency counts
    as intersection, and circle/circle tangency is allowed. Visibility is geometric:
    a small visible portion need not contain a raster pixel center.

    Radius must be positive and finite. Zero count or budget returns no circles
    with zero attempts. Every proposal, including invisible corner proposals,
    consumes an attempt. Results are deterministic for a fixed seed and NumPy
    environment; global random state is untouched. No rendering or I/O occurs.
    """
    _validate_parameters(width, height, count, radius, intensity, seed, max_attempts)
    radius = float(radius)
    rng = np.random.default_rng(seed)
    accepted: list[Circle] = []
    attempts = 0
    while len(accepted) < count and attempts < max_attempts:
        x, y = rng.uniform(
            (-radius, -radius), (width - 1 + radius, height - 1 + radius)
        )
        attempts += 1
        nearest_x = min(max(x, 0.0), width - 1)
        nearest_y = min(max(y, 0.0), height - 1)
        if hypot(x - nearest_x, y - nearest_y) > radius:
            continue
        if any(
            hypot(x - circle.center_x, y - circle.center_y) < 2 * radius
            for circle in accepted
        ):
            continue
        accepted.append(Circle(float(x), float(y), radius, intensity))
    return CirclePlacementResult(tuple(accepted), count, attempts)


def _validate_parameters(
    width: int, height: int, count: int, radius: float,
    intensity: int, seed: int, max_attempts: int,
) -> None:
    validate_integer(width, "width", 1)
    validate_integer(height, "height", 1)
    validate_integer(count, "count", 0)
    validate_integer(intensity, "intensity", 0, 255)
    validate_integer(seed, "seed", 0)
    validate_integer(max_attempts, "max_attempts", 0)
    if isinstance(radius, bool) or not isinstance(radius, Real):
        raise TypeError("radius must be a real number")
    try:
        valid_radius = isfinite(radius) and radius > 0 and isfinite(2 * float(radius))
        valid_region = isfinite(float(width) + 2 * float(radius)) and isfinite(
            float(height) + 2 * float(radius)
        )
    except OverflowError:
        valid_radius = valid_region = False
    if not valid_radius or not valid_region:
        raise ValueError("radius must be positive and sampling bounds finite in float64")
