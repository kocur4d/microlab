"""Acceptance ordering, experiment reproducibility, and archive checks."""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

from acceptance_history_experiment import collect_acceptance_history, main
from circle_placement import generate_circles


class AcceptanceHistoryTests(unittest.TestCase):
    def test_proposal_order_and_early_completion(self) -> None:
        with patch("circle_placement.np.random.default_rng") as factory:
            factory.return_value.uniform.side_effect = [
                (-1.9, -1.9), (-1, 2), (-1, 3), (-1, 6),
            ]
            result = generate_circles(8, 8, 2, 2, 45, 1, 10, record_history=True)
        self.assertEqual(result.outcomes, (False, True, False, True))
        self.assertEqual(result.attempts, 4)
        self.assertEqual(len(result.circles), 2)

    def test_empty_history(self) -> None:
        for count, budget in ((0, 10), (5, 0)):
            with self.subTest(count=count, budget=budget):
                result = generate_circles(8, 8, count, 2, 45, 1, budget, record_history=True)
                self.assertEqual(result.outcomes, ())
                self.assertEqual(result.attempts, 0)

    def test_recording_preserves_sampling(self) -> None:
        plain = generate_circles(40, 25, 1001, 3, 45, 42, 1000)
        recorded = generate_circles(40, 25, 1001, 3, 45, 42, 1000, record_history=True)
        self.assertIsNone(plain.outcomes)
        self.assertEqual(recorded.circles, plain.circles)
        self.assertEqual(recorded.attempts, plain.attempts)
        self.assertEqual(len(recorded.outcomes), 1000)
        self.assertEqual(sum(recorded.outcomes), len(recorded.circles))

    def test_invalid_record_history(self) -> None:
        with self.assertRaisesRegex(TypeError, "record_history"):
            generate_circles(8, 8, 2, 2, 45, 1, 10, record_history=1)


class AcceptanceExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outcomes = collect_acceptance_history()

    def test_shape_and_dtype(self) -> None:
        self.assertEqual(self.outcomes.shape, (80, 4000))
        self.assertEqual(self.outcomes.dtype, np.dtype(bool))

    def test_reproducibility_and_final_counts(self) -> None:
        for seed in range(80):
            with self.subTest(seed=seed):
                result = generate_circles(
                    256, 256, 4001, 15, 45, seed, 4000, record_history=True,
                )
                np.testing.assert_array_equal(self.outcomes[seed], result.outcomes)
                self.assertEqual(int(self.outcomes[seed].sum()), len(result.circles))

    def test_prefix_matches_original_observations(self) -> None:
        for filename in ("circle_counts_seeds_0-19.csv", "circle_counts_seeds_20-79.csv"):
            with (Path(__file__).parent / "experiments" / filename).open(newline="") as source:
                for observation in csv.DictReader(source):
                    seed = int(observation["seed"])
                    with self.subTest(seed=seed):
                        self.assertEqual(
                            int(self.outcomes[seed, :2000].sum()),
                            int(observation["accepted_circles"]),
                        )

    def test_save_metadata_and_prevent_overwrite(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "experiments" / "acceptance_history_seeds_0-79_attempts_4000.npz"
            with patch("acceptance_history_experiment.__file__", str(Path(directory) / "experiment.py")):
                with patch("acceptance_history_experiment.collect_acceptance_history", return_value=self.outcomes):
                    main()
                with np.load(output, allow_pickle=False) as dataset:
                    np.testing.assert_array_equal(dataset["outcomes"], self.outcomes)
                    np.testing.assert_array_equal(dataset["seeds"], np.arange(80))
                    self.assertEqual(
                        {key: dataset[key].item() for key in (
                            "width", "height", "radius", "intensity", "max_attempts", "requested_count",
                        )},
                        dict(width=256, height=256, radius=15.0, intensity=45,
                             max_attempts=4000, requested_count=4001),
                    )
                    self.assertEqual(dataset["numpy_version"].item(), np.__version__)
                    self.assertEqual(dataset["bit_generator"].item(), "PCG64")
                original = output.read_bytes()
                with patch("acceptance_history_experiment.collect_acceptance_history") as collect:
                    with self.assertRaises(FileExistsError):
                        main()
                    collect.assert_not_called()
                self.assertEqual(output.read_bytes(), original)

    def test_incomplete_run_is_rejected(self) -> None:
        from circle_placement import CirclePlacementResult

        with patch("acceptance_history_experiment.generate_circles", return_value=CirclePlacementResult((), 4001, 3999)):
            with self.assertRaisesRegex(AssertionError, "Seed 0: expected 4000 attempts, got 3999"):
                collect_acceptance_history()


if __name__ == "__main__":
    unittest.main()
