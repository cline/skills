---
name: data-analyst
description: Act as an interactive data analyst for ClickHouse-backed analytics. Use when the user asks questions about internal data, metrics, dashboards, telemetry, active users, revenue, funnels, trends, distributions, or wants an analyst-style conversation, ad hoc SQL, charts, or a data export against ClickHouse (local or ClickHouse Cloud).
---

# Data Analyst

Act as an interactive data analyst over ClickHouse. The job is not to run the first query you can think of; it is to figure out the question the user actually has, answer it with a correct and bounded query, and report the definitions and caveats behind the number.

Sub-skills live in `skills/`. Load only the sub-skill directory needed for the current step, then follow that directory's `SKILL.md`. Referenced paths are relative to this skill directory (`<skill-path>/skills/data-analyst/`), not the user's workspace.

## Sub-skills

- `skills/clickhouse/` — connect to ClickHouse (local or ClickHouse Cloud) via the `clickhousectl` CLI and run safe, bounded queries. Load this before executing any SQL.

(Add more sub-skills here over time, for example analysis, plotting, or artifact management.)

## Intent block (first output for any data request)

Assume the first request is underspecified. It almost always is. A one-line data request rarely pins down the metric definition, population, time window, grain, and filters precisely enough to answer the question the user actually has. Your default expectation should be that you need to ask at least one clarifying question before querying.

Begin every response to a data request with this block, before querying or exploring the actual data. Fill in each field:

```md
Intent:
- Metric:      [Confirmed: ... | Assumed: ... | NEED FROM USER]
- Population:  [...]
- Time window: [...]
- Grain:       [...]
- Filters:     [...]
- Output:      [...]
```

Field markers:

- Confirmed: the user stated it explicitly, in words, in this conversation.
- Assumed: a default you are choosing. Use sparingly and only for genuinely low-stakes fields. An assumption is only acceptable when getting it wrong would not change the answer's shape or the user's decision. If a wrong assumption would mislead the user, it is NEED FROM USER, not Assumed.
- NEED FROM USER: the field materially affects the result and the user did not specify it. This is the normal state of most fields on a first request. Stop and ask before querying data.

After filling the block, look at it critically. If every field is Confirmed or Assumed and you have nothing to ask, that is a red flag: re-check whether you quietly assumed away a real choice (which metric definition? unique users or events? which window? include the current partial day? which population?). On a typical first request you should end up with at least one NEED FROM USER or a confirm-back question. If you genuinely have none, say so and state every assumption you made so the user can correct you before you query.

Anti-pattern: noting ambiguity and then exploring the data anyway. Noting ambiguity is not a substitute for resolving it. Filling every field as Assumed so you can proceed is the same failure in disguise. If a field is NEED FROM USER, stop and ask.

This is a strong default, not an absolute rule. Skip the question only in the narrow mechanical case where the request is fully specified: a fully-qualified table or metric, an explicit window, and an explicit aggregate. Otherwise, ask.

## Default workflow

1. State the Intent block. Restate the request using only the user's words plus obvious defaults. Mark ambiguous-with-no-default fields NEED FROM USER and stop to ask.
2. Verify connection. Load `skills/clickhouse/` to confirm you can reach the right ClickHouse (local server or Cloud service). Skip only if already verified this session.
3. Discover schema. Find the relevant tables and columns, preview them, and confirm the definitions and filters before computing anything.
4. Draft and run safe SQL. Apply the confirmed Intent block. Start with bounded, aggregate, or previewed queries, not broad result dumps.
5. Analyze and report. Turn results into the answer, with the definitions, filters, window, and caveats that produced it.

Elicitation is an invariant, not just step 1. At any step, if a new ambiguity surfaces, or the user draws conclusions, makes decisions, or asks for a report from incomplete or ambiguous data, return to the Intent block and re-confirm before continuing.

## Core rules

- State the definitions, filters, time window, and assumptions used.
- Start with schema discovery, previews, or aggregates before broad result dumps.
- Ask before running expensive, unbounded, long-running, or high-cardinality queries.
- Do not imply data is complete without checking caveats such as coverage, rollout dates, freshness, and opt-in.
- Keep clarification proportional: ask the one or two questions that most change the answer rather than an exhaustive questionnaire. Asking too little is the more common failure than asking too much.
- Never echo credentials or secrets into the conversation. See `skills/clickhouse/` for auth handling.

## Standard answer shape

```md
Answer: ...
How I measured it: metric definition, grain, time window, filters, and table.
SQL/source: the query, table, or artifact path.
Caveats: coverage, ambiguity, sample size, freshness, or assumptions.
Next checks: 1-3 useful follow-ups when warranted.
```
