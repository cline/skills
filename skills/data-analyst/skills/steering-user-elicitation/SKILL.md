---
name: steering-user-elicitation
description: Elicit and challenge data-analysis requirements before querying. Use when the user asks ambiguous data questions, requests business/report answers, needs metric definitions clarified, or may be drawing decisions from incomplete data.
---

# Steering and User Elicitation

This skill describes how to fill the Intent block (defined in the parent `data-analyst/SKILL.md`) well, how to phrase good pushback, and how to handle metrics that are missing or commonly misunderstood.

Start from the assumption that the first request is underspecified; it almost always is. Most data requests have hidden ambiguity even when they read cleanly. Asking at least one clarifying question should be the norm; answering a first message with zero questions should be rare. The goal is productive friction, not an exhausting questionnaire.

## Filling each Intent field

For each Intent field, choose the right marker:

- Confirmed when the user stated it explicitly in this conversation.
- Assumed only for genuinely low-stakes fields where a wrong guess would not change the answer's shape or the user's decision. State the assumption so the user can correct you: "Assuming all users (no plan filter); I'll note if filtering looks needed." If a wrong guess could mislead, it is NEED FROM USER, not Assumed.
- NEED FROM USER when the field materially affects the result and the user did not specify it, the normal state of most fields on a first request. Stop and ask one targeted question.
- LOOK UP: `<term>` when the field references a term with a documented definition (a named metric, a funnel stage). Resolve it via `../reading-data-dict/` before querying; do not guess its meaning.

What each field is asking:

- Metric: what exactly should be counted, summed, averaged, or compared?
- Population: users, accounts, sessions, requests, versions, providers, or feature users?
- Time window: dates, release window, week-over-week, last N days?
- Grain: daily, weekly, per release, per user, per workspace?
- Filters: plan, platform, model/provider, version, geography, telemetry enabled?
- Output: quick answer, SQL, CSV, chart, HTML/report, or dashboard seed?

Also keep audience in mind (internal debug, exec/business update, customer/investor answer); it raises the bar for confirming definitions before presenting.

A block with no questions at all should be rare and deliberate, not the easy path. If you filled every field as Confirmed or Assumed, stop and re-check: which metric definition, which population (unique users vs events), which window (and the current partial day?), which grain? At least one of these is usually a real choice the user should make. The rule is "ask the one or two questions that most change the answer," not "find a default for everything so you can proceed."

## Good pushback

Use targeted pushback like:

- "I can answer this two ways: raw event count or unique affected users. Which do you want?"
- "This metric is only representative of telemetry-enabled users. Is directional analysis acceptable?"
- "A 2-day window may be noisy. Should I compare against the prior 2 days or prior week?"
- "Before plotting this, I want to confirm the definition of active user."

## When the metric doesn't exist

If the exact metric the user is asking for does not exist in the available data (schema, data dictionary, or known tables), do not silently substitute a proxy metric. Instead, pause and ask clarifying questions:

- "I don't see a direct metric for X. The closest available options are Y and Z, would either of these work?"
- "That metric isn't in our current schema. Can you describe what you're trying to measure so I can find the best approximation?"
- "I can approximate this using [field], but it may not match your definition exactly. Should I proceed with that caveat, or would you like to refine the request?"

## When the metric exists but the user likely means something else

The harder case is a term that is documented but commonly means different things. "Revenue" may mean billings, net, or gross; "active user" may mean any-event vs a task-creating user; a "task" may be created vs completed. When a request uses such a term:

- Mark it LOOK UP in the Intent block and resolve the documented definition.
- If the documented definition diverges from common usage, surface it before assuming: "Our `revenue` model is net of refunds, is that the figure you want, or gross billings?"
- Do not silently adopt the documented definition just because it exists. Confirm it when the divergence could change the answer or the decision.

## When to skip the full Intent block

Always produce the Intent block. You may skip asking questions (mark every field Confirmed or Assumed, none NEED FROM USER) only when the request is mechanically unambiguous. Treat this as a checkable test, not a judgment call, skip questions only if the user's message contains all of:

- a fully-qualified table or documented metric name (no interpretation needed),
- an explicit time window (a date literal or an unambiguous relative window),
- an explicit aggregate or operation (count, sum, avg, top-N, etc.).

Example that qualifies: "How many rows in `analytics.events_daily` from 2026-05-20 to 2026-05-27?"

If any of those three is missing or interpretable, at least one field is NEED FROM USER or LOOK UP, do not skip.
