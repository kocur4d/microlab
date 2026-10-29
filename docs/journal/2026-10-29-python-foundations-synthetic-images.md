# Session 01 — Python Foundations & Synthetic Images

**Date:** 2026-10-29  
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

## Issues encountered

- Python was initially unavailable in PowerShell (`py` not recognised).
- Resolved by installing Python.
- Virtual environment and NumPy/Pillow imports verified successfully.
- No remaining environment blocker.

## Verification

- **Confirmed:** Python environment reports `Environment ready!`.
- **Still to confirm explicitly:** Saved PNG output and visual inspection of the generated image.

## Next steps

1. Refactor image generation into reusable, typed Python functions.
2. Separate circle parameters from pixel manipulation.
3. Extend the generator to multiple synthetic objects.
4. Introduce reproducible random generation, followed by blur and noise.

## Quick refresher

NumPy broadcasting lets us express pixel-wise mathematics directly on coordinate arrays. A Boolean mask represents which pixels satisfy a condition; `image[mask] = value` updates those pixels.

**Resume from:** Turning the single-circle experiment into reusable Python functions.
