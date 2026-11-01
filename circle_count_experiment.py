"""Record accepted circles after 2,000 proposals for seeds 0 through 19.

Run from the project root: python circle_count_experiment.py
Execution environment: Python 3.14.7, NumPy 2.5.4.
"""

import csv
from pathlib import Path

from circle_placement import generate_circles


def main() -> None:
    """Verify each complete run and save its raw observation as CSV."""
    observations = []
    for seed in range(20):
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

    output_path = Path(__file__).parent / "experiments" / "session_03_circle_counts.csv"
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(("seed", "attempts", "accepted_circles"))
        writer.writerows(observations)


if __name__ == "__main__":
    main()
