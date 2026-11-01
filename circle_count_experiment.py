"""Record accepted circles after 2,000 proposals for a half-open seed range.

Run: python circle_count_experiment.py --start 20 --end 80
Execution environment: Python 3.14.7, NumPy 2.5.4.
"""

import argparse
import csv
from collections.abc import Sequence
from pathlib import Path

from circle_placement import generate_circles


def _parse_seeds(argv: Sequence[str] | None) -> range:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0, help="First seed (inclusive; default: 0)")
    parser.add_argument("--end", type=int, default=20, help="Stop seed (exclusive; default: 20)")
    args = parser.parse_args(argv)
    if args.start < 0:
        parser.error("--start must be nonnegative")
    if args.end <= args.start:
        parser.error("--end must be greater than --start")
    return range(args.start, args.end)


def main(argv: Sequence[str] | None = None) -> None:
    """Verify each complete run and save its raw observation as CSV."""
    seeds = _parse_seeds(argv)
    output_path = (
        Path(__file__).parent / "experiments"
        / f"circle_counts_seeds_{seeds.start}-{seeds.stop - 1}.csv"
    )
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite experiment: {output_path}")
    observations = []
    for seed in seeds:
        result = generate_circles(
            width=256,
            height=256,
            # At most one circle can be accepted per proposal, preventing early exit.
            count=2001,
            radius=15,
            intensity=45,
            seed=seed,
            max_attempts=2000,
        )
        if result.attempts != 2000:
            raise AssertionError(
                f"Seed {seed}: expected 2000 attempts, got {result.attempts}"
            )
        observations.append((seed, result.attempts, len(result.circles)))

    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("x", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(("seed", "attempts", "accepted_circles"))
        writer.writerows(observations)


if __name__ == "__main__":
    main()
