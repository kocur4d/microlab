"""Run with Python to save a reproducible random-circle image."""

from PIL import Image

from circle_placement import generate_circles
from synthetic_image import generate_image


def main() -> None:
    """Render a fixed-seed placement experiment to random_circles.png."""
    width, height = 256, 256
    result = generate_circles(
        width, height, count=30, radius=15, intensity=45,
        seed=42, max_attempts=2000,
    )
    image = generate_image(width, height, result.circles)
    Image.fromarray(image).save("random_circles.png")
    print(f"Accepted {len(result.circles)}/{result.requested_count} circles "
          f"in {result.attempts} attempts")


if __name__ == "__main__":
    main()
