# Session 02 — Practical Statistical Modelling

**Date:** 2026-10-30  
**Project:** Microlab  
**Status:** Question defined; experiment not yet performed

## Direction and decisions

- Move from an informal observation to a precise **question → random variable → mechanism → estimand → method → interpretation**.
- Learn statistical modelling through small computational experiments using the existing circle-placement algorithm.
- Discontinue the previous 80-trial population sweep. The user reports resetting the repository to the latest GitHub main branch. This direction supersedes Session 01's population-sweep next step; its conceptual lessons remain relevant.

## Conceptual lessons

- **Geometric capacity versus algorithmic efficiency:** what can fit geometrically differs from what this sequential random algorithm accepts within a finite proposal budget. Budget exhaustion does not establish maximum packing capacity.
- **Scale and dimensionless geometry:** compare geometry through ratios such as field dimensions relative to radius. Scale invariance requires consistent scaling of the continuous field and proposal rules; pixel-coordinate conventions matter. Attempt budgets and stopping rules must also be specified for meaningful comparisons.
- **History versus next-proposal probability:** observing 30 acceptances in 61 attempts gives a historical cumulative rate, not the probability of accepting the next proposal. The current arrangement determines the remaining admissible proposal region.
- **Conditional versus averaged probability:** acceptance probability for one frozen arrangement differs from a probability averaged over random arrangements produced by the algorithm.
- **Probability models depend on the mechanism:** one acceptance indicator is Bernoulli; successes in a fixed number of independent proposals against unchanged geometry are binomial; proposals until the first acceptance against frozen geometry have a geometric waiting-time model (counting the successful proposal, with positive acceptance probability). Updating the arrangement after acceptance changes the probability, so a full evolving run is not automatically a fixed-probability binomial experiment.
- Recognising when a probability model applies is itself a skill to practise. Simulation can estimate properties of an unknown distribution without first assuming a parametric family.

## First precise research question

> What is the expected number of circles accepted by our rejection-sampling algorithm within 2,000 attempts, for a 256×256 field and radius 15?

- **Random variable:** `C_2000`, the number of geometrically visible circles accepted after 2,000 proposals in a fresh run, under the existing field-of-view and full-circle non-overlap rules.
- **Mechanism:** sequential random proposals; accepted circles change the geometry for later proposals. Preserve the existing algorithm and boundary conventions.
- **Estimand:** `E[C_2000]`, averaging over independent random proposal sequences from an initially empty field.
- **Initial estimator:** the sample mean of `C_2000` across independent full runs, using explicitly recorded seeds. Do not stop early on reaching a small requested population; ensure each run actually consumes the full 2,000-attempt budget.
- **Interpretation:** expected output of this algorithm under this fixed geometry and budget. It does not directly estimate geometric capacity or conditional next-proposal acceptance probability.

## Status and next step

- **Established in discussion:** research question, estimand, and initial estimation method.
- **Not yet performed:** the new repeated-run experiment; no estimate of `E[C_2000]` or distributional conclusion is recorded here. Earlier example counts are not results for this question.
- **Next concrete step:** agree on the number of independent runs and seed list, then implement a minimal experiment that records accepted count and verifies 2,000 attempts per run before computing the sample mean.
- **Revisit later:** conditional acceptance probabilities, variability, waiting times, and predictive modelling.
