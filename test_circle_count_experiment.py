"""CLI bounds, output naming, and preservation checks for the experiment."""

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from circle_count_experiment import _parse_seeds, main
from circle_placement import CirclePlacementResult


class CircleCountExperimentTests(unittest.TestCase):
    def test_default_seeds(self) -> None:
        self.assertEqual(_parse_seeds([]), range(0, 20))

    def test_explicit_half_open_range(self) -> None:
        self.assertEqual(_parse_seeds(["--start", "20", "--end", "80"]), range(20, 80))

    def test_invalid_arguments(self) -> None:
        for argv in (
            ["--start", "-1"],
            ["--start", "20", "--end", "20"],
            ["--start", "21", "--end", "20"],
            ["--end", "-1"],
            ["--start", "1.5"],
            ["--end", "abc"],
            ["--start"],
            ["--unknown"],
        ):
            with self.subTest(argv=argv), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as error:
                    _parse_seeds(argv)
                self.assertEqual(error.exception.code, 2)

    def test_output_names_and_contents(self) -> None:
        for start, end, filename, expected in (
            (20, 22, "circle_counts_seeds_20-21.csv",
             "seed,attempts,accepted_circles\n20,2000,0\n21,2000,0\n"),
            (0, 1, "circle_counts_seeds_0-0.csv",
             "seed,attempts,accepted_circles\n0,2000,0\n"),
        ):
            with self.subTest(start=start), TemporaryDirectory() as directory:
                with patch("circle_count_experiment.__file__", str(Path(directory) / "experiment.py")):
                    with patch("circle_count_experiment.generate_circles", return_value=CirclePlacementResult((), 2001, 2000)) as generate:
                        main(["--start", str(start), "--end", str(end)])
                    self.assertEqual(
                        [call.kwargs["seed"] for call in generate.call_args_list],
                        list(range(start, end)),
                    )
                self.assertEqual(
                    (Path(directory) / "experiments" / filename).read_text(), expected,
                )

    def test_existing_output_is_preserved(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "experiments" / "circle_counts_seeds_20-79.csv"
            output.parent.mkdir()
            output.write_bytes(b"original observations\r\n")
            with patch("circle_count_experiment.__file__", str(Path(directory) / "experiment.py")):
                with patch("circle_count_experiment.generate_circles") as generate:
                    with self.assertRaises(FileExistsError):
                        main(["--start", "20", "--end", "80"])
                    generate.assert_not_called()
            self.assertEqual(output.read_bytes(), b"original observations\r\n")

    def test_incomplete_budget_does_not_save_output(self) -> None:
        with TemporaryDirectory() as directory:
            with patch("circle_count_experiment.__file__", str(Path(directory) / "experiment.py")):
                with patch("circle_count_experiment.generate_circles", return_value=CirclePlacementResult((), 2001, 1999)):
                    with self.assertRaisesRegex(AssertionError, "Seed 0: expected 2000 attempts, got 1999"):
                        main(["--start", "0", "--end", "1"])
            self.assertFalse((Path(directory) / "experiments").exists())


if __name__ == "__main__":
    unittest.main()
