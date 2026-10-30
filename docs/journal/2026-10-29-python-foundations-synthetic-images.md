# Session 01 — Python Foundations & Synthetic Images

**Date:** 2026-10-29  
**Updated:** 2026-10-30  
**Project:** Microlab  
**Status:** In progress

## Goal

Establish a Python scientific computing environment and understand how synthetic grayscale images can be represented and generated using NumPy.

## What we covered

- Installed Python on Windows and created a project-local virtual environment (`.venv`).
- Installed and successfully imported NumPy and Pillow.
- Explored a 256 × 256 synthetic grayscale image containing a circular object.
- Used `np.full()` to initialise image pixels.
- Used `np.ogrid` to create coordinate arrays.
- Used NumPy broadcasting to compute a Boolean circle mask.
- Used Boolean indexing to assign pixel intensities.

## Important concepts learned

**Images as arrays**

- A grayscale image is a 2D numerical array.
- Array indexing follows `image[y, x]`.
- Coordinates increase rightwards (x) and downwards (y).
- `uint8` represents intensities from 0 to 255.

**Broadcasting**

The most important new concept of this session.

```python
y, x = np.ogrid[:height, :width]

mask = (
    (x - center_x)**2
    + (y - center_y)**2
    <= radius**2
)

image[mask] = 45
```

Mental model:

- `x` is a horizontal coordinate vector with shape `(1, width)`.
- `y` is a vertical coordinate vector with shape `(height, 1)`.
- NumPy broadcasts the operations to the full image dimensions.
- The result is a 2D Boolean array.
- Boolean indexing selects pixels to modify.

**Connection to JavaScript:** Conceptually equivalent to nested iteration or mapping over x/y coordinates. NumPy performs the element-wise operations internally rather than requiring explicit Python loops.

This initially felt unfamiliar because x and y looked like scalar variables, but thinking of them as vectors made the operation intuitive.

## Engineering decisions

- Begin with simple, controlled synthetic images before real microscopy data.
- Use NumPy arrays as the image's numerical representation.
- Adopt explicit image coordinate conventions.
- Keep the initial experiments independent of FastAPI and React.
- Build incrementally, prioritising understanding over scaffolding.
- Separate scientific model assumptions, geometry generation, and pixel rendering. The renderer permits overlaps (later circles overwrite earlier ones); placement determines whether overlaps are allowed.
- Treat the image as a field of view into a larger sample. Sample centres from the visible rectangle `[0, width - 1] × [0, height - 1]` extended by the radius, rejecting circles that do not intersect it. Outside centres and partial visibility are valid; requested count means geometrically visible circles.
- Enforce non-overlap using full circle geometry, including portions outside the field. Circle tangency is allowed.
- Use one global proposal budget, counting every rejection. Return partial results with metadata when exhausted rather than treating crowding as an error.
- Prefer predictable, non-mutating public interfaces. Allocate and mutate internally owned arrays for efficiency, then transfer ownership to the caller; never modify caller inputs.
- Keep placement simple; defer a strategy interface until multiple concrete algorithms justify it.

## Implementation milestones

- `synthetic_image.py`: reusable, typed `generate_image()` and frozen `Circle` definitions; supports multiple circles, with saving and printing separate from generation.
- `circle_placement.py`: seeded rejection sampling using a local NumPy RNG. Returns immutable accepted circles, requested count, and total attempts; accepted count is derived from the circles.
- `validation.py`: shared integer validation. `random_circles_example.py` connects placement to rendering without coupling their implementations.
- Tests cover geometry, boundaries, overlaps, array ownership, reproducibility, unchanged global RNG state, validation, and partial results.

## Further concepts learned

- `np.hypot(dx, dy)` computes Euclidean distance without explicitly squaring large coordinates. The renderer now uses it instead of the introductory squared-distance mask above.
- `rng.uniform(low, high)` accepts array-like bounds and samples each coordinate using its corresponding bounds. `x, y = ...` unpacks the result, resembling JavaScript destructuring.
- Rejection sampling proposes candidates and discards invalid ones. As space fills, finding an acceptable position becomes harder; the size of this effect remains to be measured.
- Geometric intersection differs from raster visibility: a tiny intersecting circle portion may contain no pixel centre and therefore draw no pixels. Tangency counts as geometric intersection in the current model.

## Workflow decisions

- ChatGPT acts as scientific/technical supervisor for theory, architecture, and experiment design; Codex implements and tests.
- The user verifies results locally and handles commits and pushes to GitHub. ChatGPT reviews committed code through the user-reported verified GitHub integration; that integration was not exercised during this journal update.
- Preserve conceptual learning: discuss and understand the model and algorithms rather than delegating all understanding.

## Issues encountered

- Python was initially unavailable in PowerShell (`py` not recognised).
- Resolved by installing Python.
- Virtual environment and NumPy/Pillow imports verified successfully.
- No remaining environment blocker.

## Verification

- **Confirmed:** Python environment reports `Environment ready!`.
- **Verified again on 2026-10-30:** `.venv\Scripts\python.exe -m unittest discover -v` passed all 15 tests (8 renderer, 7 placement).
- **Previously executed:** The random-circle example reported 30/30 accepted in 61 attempts with a 256 × 256 field, radius 15, intensity 45, seed 42, and global budget 2000; it saved `random_circles.png`. Not rerun for this update.
- **Still unconfirmed:** Visual inspection of the saved images. Passing tests does not establish segmentation accuracy or spatial neutrality of the placement process.

## Deferred discussion

- How partial visibility and boundary objects influence segmentation accuracy.
- Whether the placement process introduces spatial bias.

## Next steps

1. **Planned, not executed:** Investigate rejection sampling under increasing crowding. Hold field dimensions, radius, intensity, and global attempt budget fixed; increase requested population and record requested count, accepted count, and actual attempts with explicit seeds.
2. Compare completion and budget exhaustion across populations and repeat seeds to distinguish crowding trends from individual random outcomes.
3. Keep blur and noise as later extensions after understanding placement behaviour.

## Quick refresher

NumPy broadcasting lets us express pixel-wise mathematics directly on coordinate arrays. A Boolean mask represents which pixels satisfy a condition; `image[mask] = value` updates those pixels.

**Resume from:** Designing the population sweep for the crowding experiment, using the existing `generate_circles()` result metadata.
