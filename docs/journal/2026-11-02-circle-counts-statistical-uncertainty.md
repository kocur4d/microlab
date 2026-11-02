# Session 03 — Circle Counts, Estimation & Statistical Uncertainty

**Date:** 2026-11-01–2026-11-02  
**Project:** Microlab  
**Status:** Experiment completed; interpretation recorded

## Question and method

> What is the expected number of circles accepted in 2,000 proposals for a 256 × 256 field and radius 15?

- Continue the framework: **question → random variable → mechanism → estimand → method → interpretation**.
- **Random variable:** `C_2000`, the accepted count in one complete run from an empty field. **Estimand:** `E[C_2000]`, estimated by the sample mean over independent seeded runs.
- Preserve sequential rejection sampling, geometric visibility, and full-circle non-overlap. This estimates the algorithm's finite-budget output, not maximum packing capacity.
- Configuration: width and height 256, radius 15, intensity 45, exactly 2,000 proposals. Request 2,001 circles so reaching the requested count cannot end a run early.

## Work and decisions

- `circle_count_experiment.py` accepts half-open seed ranges, checks that every run consumes 2,000 attempts, and records seed, attempts, and accepted count.
- Preserve raw observations and refuse overwriting existing CSV files. Seed ranges appear in filenames; the original 20 observations were retained when adding 60 runs.
- Data: `experiments/circle_counts_seeds_0-19.csv` and `experiments/circle_counts_seeds_20-79.csv`.
- Use explicit seeds for reproducibility, keep statistical interpretation separate from simulation implementation, and record predictions before inspecting additional results.
- The supplied session notes identify commit `093c4e9543f359c10cc164e3457cd33fa36ab821` as relevant; that association was not independently checked for this entry.

## Results

The session reported these summaries; the journal review confirmed the script configuration and the 80 stored observations, each recording 2,000 attempts. Simulations and confidence-interval calculations were not rerun for this entry.

| Statistic | First 20 runs | All 80 runs |
|---|---:|---:|
| Sample mean | 63.600 | 63.363 |
| Sample standard deviation | 1.392 | 1.844 |
| Standard error | 0.311 | 0.206 |
| Approximate 95% t-confidence interval | [62.949, 64.251] | [62.952, 63.773] |
| Observed count range | 61–66 | 59–67 |

- **Prediction:** quadrupling the sample size would approximately halve the standard error if the estimated standard deviation remained similar, and narrow the confidence interval.
- **Observed:** standard deviation increased; standard error fell by about 34%, rather than 50%, and the interval narrowed. The first 20 runs showed less variability than the combined sample; this does not establish a change in the algorithm.

## Lessons

- **Standard deviation versus standard error:** `s` estimates variability between individual runs; `SE = s / sqrt(n)` estimates variability of the sample mean across repeated experiments of size `n`. More runs improve estimation precision without making individual runs less random.
- **Computational cost of precision:** holding variability constant, halving SE requires roughly four times as many independent runs; reducing it tenfold requires roughly 100 times as many. Realised estimates need not follow this scaling exactly because `s` also changes.
- **Sample variance:** dividing by `n - 1` does not make variance systematically shrink as observations accumulate; the sum of squared deviations also grows. Fitting the sample mean constrains deviations to sum to zero, leaving `n - 1` degrees of freedom. Bessel's correction makes sample variance unbiased for IID observations with finite variance; a proof is deferred.
- **Student's t:** reviewed the t-statistic, unknown population standard deviation, `n - 1` degrees of freedom, the `0.975` quantile for a two-sided 95% interval, and the relationship to one-sample t-tests. The intervals here are approximate because normality of the discrete count distribution has not been established.
- **Confidence-interval interpretation:** the mean is fixed and sample-based intervals vary. Under its assumptions, a 95% procedure covers the mean in approximately 95% of repeated experiments. It does not describe where 95% of individual runs fall or assign a frequentist 95% probability to the fixed mean lying in this realised interval. Distinguish confidence, prediction, and Bayesian credible intervals.

## Open questions

- Why does the algorithm typically accept around 63 circles within this budget?
- How does crowding change acceptance probability, and how does a particular arrangement determine the admissible region for the next proposal?
- How does probability conditional on a frozen arrangement differ from probability averaged over random arrangements?
- Can accepted counts be predicted for other radii, field dimensions, or proposal budgets?

## Next step

Investigate the probability of accepting the next proposal given a particular existing circle arrangement. Define the conditional probability and proposal geometry before choosing an estimation method.
