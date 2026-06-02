---
name: analyzer
description: Analyze queried data for trends, week-over-week comparisons, distributions, funnels, cohorts, top-N lists, anomalies, sanity checks, and report-ready findings. Use after or alongside ClickHouse queries when the user wants insight rather than raw rows.
---

# Analyzer

Turn data into defensible findings instead of only returning rows.

## Analysis patterns

Choose the smallest pattern that answers the question:

- Trend: metric over time at the right grain.
- Comparison: current period vs prior period, release vs baseline, or segment A vs B.
- Distribution: percentiles, skew, tails, and outliers.
- Funnel: step counts, conversion rates, and drop-offs.
- Cohort: behavior grouped by start date, version, source, or first action.
- Top-N: largest contributors with share of total.
- Sanity check: row counts, null rates, first/last seen, duplicates, and data freshness.

## Before concluding

- Verify the time window and grain match the user's question.
- Check sample size, nulls, and whether the metric is dominated by a small tail.
- Look for freshness, rollout, telemetry opt-in, or version-coverage issues.
- Avoid causal language unless the query design supports causality.
- If the result is surprising, run or propose one validation query before presenting it as fact.

## Finding format

```md
Finding: ...
Evidence: ...
Confidence: High/Medium/Low because ...
Caveats: ...
Recommended next check: ...
```
