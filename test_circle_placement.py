"""Geometry, budget, and reproducibility checks for circle placement."""

from itertools import combinations
from math import hypot
import unittest
from unittest.mock import patch

import numpy as np

from circle_placement import CirclePlacementResult, generate_circles
from synthetic_image import Circle, generate_image


class CirclePlacementTests(unittest.TestCase):
    def test_visible_geometry_and_non_overlap(self) -> None:
        result = generate_circles(40, 25, 20, 3, 45, 42, 1000)
        self.assertEqual(len(result.circles), 20)
        self.assertLessEqual(result.attempts, 1000)
        for circle in result.circles:
            self.assertGreaterEqual(circle.center_x, -3)
            self.assertLessEqual(circle.center_x, 42)
            self.assertGreaterEqual(circle.center_y, -3)
            self.assertLessEqual(circle.center_y, 27)
            nearest_x = min(max(circle.center_x, 0), 39)
            nearest_y = min(max(circle.center_y, 0), 24)
            # Absolute tolerance is in pixels, far below the pixel sampling scale.
            self.assertLessEqual(
                hypot(circle.center_x - nearest_x, circle.center_y - nearest_y),
                3 + 1e-12,
            )
            self.assertEqual((circle.radius, circle.intensity), (3, 45))
        for first, second in combinations(result.circles, 2):
            self.assertGreaterEqual(
                hypot(first.center_x - second.center_x, first.center_y - second.center_y),
                6 - 1e-12,
            )

    def test_reproducibility_and_local_random_state(self) -> None:
        global_state = np.random.get_state()
        first = generate_circles(40, 25, 10, 3, 45, 42, 100)
        second = generate_circles(40, 25, 10, 3, 45, 42, 100)
        different = generate_circles(40, 25, 10, 3, 45, 43, 100)
        self.assertEqual(first, second)
        self.assertNotEqual(first.circles, different.circles)
        after = np.random.get_state()
        self.assertEqual(global_state[0], after[0])
        np.testing.assert_array_equal(global_state[1], after[1])
        self.assertEqual(global_state[2:], after[2:])

    def test_corner_rejection_outside_centers_and_full_geometry(self) -> None:
        with patch("circle_placement.np.random.default_rng") as factory:
            factory.return_value.uniform.side_effect = [
                (-1.9, -1.9),  # In the proposal box, outside the rounded corner.
                (-1, 2),      # Visible with center outside the image.
                (-1, 3),      # Overlaps the first circle in full geometry.
                (-1, 6),      # Tangent to the first circle.
            ]
            result = generate_circles(8, 8, 2, 2, 45, 1, 10)
            factory.return_value.uniform.assert_called_with((-2.0, -2.0), (9.0, 9.0))
        self.assertEqual(result, CirclePlacementResult(
            (Circle(-1, 2, 2, 45), Circle(-1, 6, 2, 45)), 2, 4,
        ))
        image = generate_image(8, 8, result.circles)
        self.assertTrue(np.any(image == 45))

    def test_global_budget_returns_partial_result(self) -> None:
        with patch("circle_placement.np.random.default_rng") as factory:
            factory.return_value.uniform.return_value = (1, 1)
            result = generate_circles(4, 4, 3, 1, 90, 42, 5)
            self.assertEqual(factory.return_value.uniform.call_count, 5)
        self.assertEqual(result, CirclePlacementResult((Circle(1, 1, 1, 90),), 3, 5))

    def test_zero_count_or_budget(self) -> None:
        self.assertEqual(
            generate_circles(2, 2, 0, 1, 45, 42, 10),
            CirclePlacementResult((), 0, 0),
        )
        self.assertEqual(
            generate_circles(2, 2, 5, 1, 45, 42, 0),
            CirclePlacementResult((), 5, 0),
        )

    def test_single_pixel_field_and_radius_larger_than_image(self) -> None:
        with patch("circle_placement.np.random.default_rng") as factory:
            factory.return_value.uniform.side_effect = [(9, 9), (-10, 0)]
            result = generate_circles(1, 1, 1, 10, 0, 42, 2)
        self.assertEqual(result, CirclePlacementResult((Circle(-10, 0, 10, 0),), 1, 2))
        np.testing.assert_array_equal(generate_image(1, 1, result.circles), [[0]])

    def test_invalid_inputs(self) -> None:
        defaults = dict(width=10, height=10, count=2, radius=1, intensity=45,
                        seed=42, max_attempts=10)
        cases = [
            ("width", 0, ValueError), ("height", -1, ValueError),
            ("width", True, TypeError), ("height", 1.5, TypeError),
            ("count", -1, ValueError), ("count", 1.5, TypeError),
            ("radius", 0, ValueError), ("radius", -1, ValueError),
            ("radius", float("nan"), ValueError),
            ("radius", float("inf"), ValueError),
            ("radius", 1e308, ValueError),
            ("radius", "1", TypeError), ("radius", True, TypeError),
            ("intensity", 256, ValueError), ("intensity", -1, ValueError),
            ("intensity", 1.5, TypeError), ("seed", -1, ValueError),
            ("seed", None, TypeError), ("seed", True, TypeError),
            ("max_attempts", -1, ValueError), ("max_attempts", 1.5, TypeError),
        ]
        for name, value, error in cases:
            with self.subTest(name=name, value=value):
                with self.assertRaises(error):
                    generate_circles(**(defaults | {name: value}))


if __name__ == "__main__":
    unittest.main()
