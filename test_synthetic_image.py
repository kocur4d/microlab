"""Behavioral tests for deterministic grayscale generation."""

import unittest

import numpy as np

from synthetic_image import Circle, generate_image


class GenerateImageTests(unittest.TestCase):
    def test_empty_scene(self) -> None:
        image = generate_image(3, 2, [], background=255)
        self.assertEqual(image.shape, (2, 3))
        self.assertEqual(image.dtype, np.dtype("uint8"))
        np.testing.assert_array_equal(image, [[255, 255, 255], [255, 255, 255]])

    def test_xy_coordinates_and_included_boundary(self) -> None:
        image = generate_image(5, 3, [Circle(3, 1, 1, 45)])
        np.testing.assert_array_equal(image, [
            [200, 200, 200, 45, 200],
            [200, 200, 45, 45, 45],
            [200, 200, 200, 45, 200],
        ])

    def test_multiple_circles_clipping_and_overlap_order(self) -> None:
        image = generate_image(4, 3, [Circle(0, 0, 1, 45), Circle(1, 0, 1, 90)])
        np.testing.assert_array_equal(image, [
            [90, 90, 90, 200], [45, 90, 200, 200], [200, 200, 200, 200],
        ])

    def test_fractional_zero_radius_and_outside_circles(self) -> None:
        image = generate_image(3, 2, [
            Circle(0.5, 0, 0.5, 0), Circle(2, 1, 0, 255), Circle(-3, -3, 1, 90),
        ])
        np.testing.assert_array_equal(image, [[0, 0, 200], [200, 200, 255]])

    def test_large_geometry_does_not_overflow(self) -> None:
        image = generate_image(2, 1, [Circle(1e200, 0, 1e200, 45)])
        np.testing.assert_array_equal(image, [[45, 45]])

    def test_results_are_independently_owned_and_inputs_unchanged(self) -> None:
        circles = [Circle(1, 0, 0, 45)]
        first = generate_image(2, 1, circles)
        second = generate_image(2, 1, circles)
        self.assertTrue(first.flags.owndata)
        self.assertFalse(np.shares_memory(first, second))
        first[:] = 0
        np.testing.assert_array_equal(second, [[200, 45]])
        self.assertEqual(circles, [Circle(1, 0, 0, 45)])

    def test_invalid_image_inputs(self) -> None:
        cases = [
            ({"width": 0}, ValueError),
            ({"height": -1}, ValueError),
            ({"width": 2.5}, TypeError),
            ({"height": True}, TypeError),
            ({"background": -1}, ValueError),
            ({"background": 256}, ValueError),
            ({"background": 1.5}, TypeError),
            ({"circles": None}, TypeError),
            ({"circles": [None]}, TypeError),
        ]
        for overrides, error in cases:
            with self.subTest(overrides=overrides):
                arguments = {"width": 3, "height": 2, "circles": []} | overrides
                with self.assertRaises(error):
                    generate_image(**arguments)

    def test_invalid_circle_parameters(self) -> None:
        cases = [
            (Circle(float("nan"), 0, 1, 45), ValueError),
            (Circle(0, float("inf"), 1, 45), ValueError),
            (Circle(0, 0, float("inf"), 45), ValueError),
            (Circle(0, 0, -1, 45), ValueError),
            (Circle("x", 0, 1, 45), TypeError),
            (Circle(0, 0, True, 45), TypeError),
            (Circle(0, 0, 1, 256), ValueError),
            (Circle(0, 0, 1, -1), ValueError),
            (Circle(0, 0, 1, 45.5), TypeError),
            (Circle(0, 0, 1, True), TypeError),
        ]
        for circle, error in cases:
            with self.subTest(circle=circle):
                with self.assertRaises(error):
                    generate_image(3, 2, [circle])


if __name__ == "__main__":
    unittest.main()
