"""Collect fixed-budget acceptance histories without statistical analysis.

Run: python acceptance_history_experiment.py
Output: experiments/acceptance_history_seeds_0-79_attempts_4000.npz
"""

from pathlib import Path
import platform

import numpy as np
from numpy.typing import NDArray

from circle_placement import generate_circles


SEEDS = tuple(range(80))
WIDTH = 256
HEIGHT = 256
RADIUS = 15.0
INTENSITY = 45
MAX_ATTEMPTS = 4000
# More requested circles than proposals guarantees budget exhaustion.
REQUESTED_COUNT = MAX_ATTEMPTS + 1


def collect_acceptance_history() -> NDArray[np.bool_]:
    """Return outcomes[run, attempt] for the fixed experiment, in seed order.

    Every run starts empty. Row i uses SEEDS[i]; column zero is proposal one.
    Geometry and local random generation are provided by the existing sampler.
    """
    outcomes = np.empty((len(SEEDS), MAX_ATTEMPTS), dtype=np.bool_)
    for row, seed in enumerate(SEEDS):
        result = generate_circles(
            width=WIDTH, height=HEIGHT, count=REQUESTED_COUNT, radius=RADIUS,
            intensity=INTENSITY, seed=seed, max_attempts=MAX_ATTEMPTS,
            record_history=True,
        )
        if result.attempts != MAX_ATTEMPTS:
            raise AssertionError(
                f"Seed {seed}: expected {MAX_ATTEMPTS} attempts, got {result.attempts}"
            )
        if result.outcomes is None or len(result.outcomes) != MAX_ATTEMPTS:
            raise AssertionError(f"Seed {seed}: missing or incomplete acceptance history")
        if sum(result.outcomes) != len(result.circles):
            raise AssertionError(f"Seed {seed}: acceptance history disagrees with circles")
        outcomes[row] = result.outcomes
    return outcomes


def main() -> None:
    """Collect and exclusively save observations and reproducibility metadata."""
    output_path = (
        Path(__file__).parent / "experiments"
        / "acceptance_history_seeds_0-79_attempts_4000.npz"
    )
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite experiment: {output_path}")
    outcomes = collect_acceptance_history()
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("xb") as output:
        np.savez_compressed(
            output, outcomes=outcomes, seeds=np.array(SEEDS, dtype=np.int64),
            width=WIDTH, height=HEIGHT, radius=RADIUS, intensity=INTENSITY,
            max_attempts=MAX_ATTEMPTS, requested_count=REQUESTED_COUNT,
            python_version=platform.python_version(), numpy_version=np.__version__,
            bit_generator="PCG64",
        )


if __name__ == "__main__":
    main()
