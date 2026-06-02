---
name: reading-data-dict
description: Read project data documentation (data dictionaries, dbt manifests, model docs, column descriptions, lineage, metric definitions) before writing analytics SQL. Use for mapping business and product terms to concrete models and columns.
---

# Reading Data Dictionary

Use this before writing SQL for documented metrics, so that business and product terms map to the right models, columns, and definitions instead of guesses.

When invoked from the elicitation flow to resolve specific LOOK UP terms, scope the work to those terms: resolve their definitions and surface any options/candidates back to the user. Do not perform a full data exploration unless the user explicitly asked for one or no curated model is obvious.

## Where the definitions live

This skill is generic. A project may document its data in one or more of:

- a dbt project (model `.sql`, `models/**/*.yml`, `target/manifest.json`, generated docs)
- a dedicated data dictionary directory (for example `data_dictionary/**`)
- metric or semantic-model YAML files
- a BI tool's metric layer, a wiki, or a README

If your team has a canonical source (for example a dbt repository), treat it as the source of truth and point this skill at it. Prefer reading it over the remote `gh` API or a fresh checkout rather than relying on a possibly-stale local clone.

Useful artifacts to inspect first, when present:

- `data_dictionary/**`
- `target/manifest.json`
- `models/**/*.yml`
- `models/**/*.sql`
- metric or semantic model YAML files

## Procedure

1. Locate the documentation source, stopping at the first that works:
   - Canonical docs repo (preferred). If the team has one, read files directly without cloning. With the `gh` CLI:
     ```bash
     # List a directory
     gh api repos/<org>/<dbt-repo>/contents/data_dictionary

     # Read a specific file
     gh api repos/<org>/<dbt-repo>/contents/data_dictionary/some-file.md \
       --jq '.content' | base64 -d
     ```
     Fetch `data_dictionary/**` files selectively before any model SQL or YAMLs.
   - Local clone (fallback). If `gh` is unavailable or unauthenticated, check for a local directory whose `git remote -v` matches the canonical repo. Use it only if it is sufficiently up to date.
   - ClickHouse schema fallback. If no documentation source is available, discover the schema directly (see `../clickhouse/`). Prefer curated models (commonly named `gold_*`, `silver_*`, `fct_*`, `dim_*`) over raw event or log tables. State explicitly that you fell back to the live schema and have no documented definition.
2. Inspect relevant `data_dictionary/**` files first, then locate models, model docs, manifest entries, column descriptions, lineage, or metric docs for the requested concept.
3. Identify the curated model first. Use raw event tables only when no curated model exists, the curated model is insufficient, or the user explicitly requests raw data.
4. Extract the exact definitions for:
   - metric name
   - entity/population
   - grain and time window
   - filters and exclusions
   - required columns
   - safe join keys/patterns
   - freshness, rollout, or coverage caveats
5. Cross-check lineage when the model is derived from raw events.
6. Summarize definitions back to the user when they affect interpretation.

If no relevant data dictionary entry exists, say so explicitly and continue with model docs, manifest metadata, and SQL lineage. If the data dictionary conflicts with model docs or the observed schema, surface the discrepancy before writing SQL.

## Definition summary template

```md
Definitions used:
- Metric: ...
- Population: ...
- Grain/window: ...
- Model/table: ...
- Key columns: ...
- Joins: ...
- Known caveats: ...
```

## Bias toward documented semantics

If a term like "active user," "daily active," "tokens," "revenue," "timeout," "telemetry," "retention," or "funnel" appears, do not invent a definition. Find a documented definition or ask the user to choose one.
