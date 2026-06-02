---
name: plotting
description: Create standardized charts and visual assets from analytics query results. Prefer dependency-free plain HTML/CSS/JavaScript/SVG for interactive exploratory charts; use local plotting tools such as matplotlib, seaborn, or Plotly when static/report-ready exports or specialized charting libraries are more appropriate. Use for trends, comparisons, distributions, report assets, CSV-to-chart work, and presentation-ready data visuals.
---

# Plotting

Create charts when they make the analysis easier to understand or when the user requests a report/presentation artifact.

First goal: create a useful local plot artifact from a bounded query result. Do not turn a plotting request into a dashboard, presentation builder, or broad report unless the user explicitly asks for that.

## When to plot

Plot for:

- time-series trends
- before/after comparisons
- segment comparisons
- distributions and percentiles
- funnels
- presentation/report assets

Avoid plotting when the metric definition or query is still uncertain unless the chart is clearly labeled exploratory.

Do not show charts too early by default when doing exploratory analysis if the metric, population, time window, or grouping could bias interpretation. Prefer one concise clarification question or an explicitly labeled exploratory chart.

## Plot intent contract

Before generating a plot, know or infer:

- chart type
- x-axis
- y-axis / primary metric
- grouping, color, or breakdown dimension
- time window and filters
- source query/model/table
- audience: exploratory, report-ready, presentation/blog asset, or quick internal check

If the mapping is obvious from the user's request or the result shape, proceed and state the inferred mapping in the response. If multiple reasonable mappings exist, ask one concise clarification question before plotting. For report-ready or presentation assets, confirm ambiguous choices before generating.

Keep simple plotting requests lightweight. Do not ask an exhaustive questionnaire when the user has already provided enough context.

## Default chart selection

Use these defaults unless the user asks otherwise:

| Result shape | Default chart |
| --- | --- |
| date/time + one numeric metric | line chart |
| date/time + one numeric metric + one low-cardinality category | multi-line chart colored by category |
| category + one numeric metric | sorted bar chart |
| ordered funnel/stage + count or rate | ordered bar or funnel-style chart |
| numeric distribution | histogram or box plot; ask if the intended distribution view is unclear |
| multiple numeric metrics | ask which metric to emphasize unless one is clearly primary |

For high-cardinality categories, choose a bounded top-N only when the ranking metric is clear. Default to top 5 for multi-line time series and top 10 for bar charts. State the top-N rule in the caveats.

Choose the chart based on analytical intent, not only result shape:

- Trend over time: line chart, small multiples, slope chart, or indexed trend.
- Compare categories/rankings: sorted bar, dot plot, or lollipop.
- Part-to-whole: stacked bar/area only when composition is the point; avoid pie/donut except for very simple cases.
- Distribution: histogram, box plot, violin, strip/beeswarm, or percentile summary.
- Relationship: scatterplot, heatmap, or connected scatter when order matters.

If the intended message is unclear, ask one concise question such as: "Should this emphasize absolute volume, trend shape, ranking, composition, distribution, or relationship?"

## Complexity limits for the first pass

- Use one x-axis and one primary y-axis by default.
- Use at most one grouping/color dimension by default.
- Avoid dual-axis charts unless explicitly requested.
- Avoid dense legends, many small multiples, or complex multi-measure charts in the first pass.
- Prefer basic line and bar charts for MVP plotting.
- For interactive MVP plotting, do not default to Plotly. Prefer plain HTML/CSS/JavaScript/SVG unless the user requests a specific charting library or the interaction would be unreasonably complex to implement cleanly.
- Include uncertainty/error bars only when the query explicitly provides uncertainty values or the user asks for them.
- If a chart would need substantial transformation or statistical modeling, explain the needed transformation before generating it.

Avoid common chart traps:

- Do not create spaghetti charts. If a time-series chart has too many lines, overlapping lines, or hard-to-read labels, reduce to top-N, highlight a subset, facet into small multiples, or ask what to focus on.
- Do not use a log scale as the automatic fix for one dominant series. Use log scale only when multiplicative/rate-of-change comparison is the intended message, and label it clearly.
- Do not use dual axes to compare unrelated metrics. Use separate panels, normalization, percent change, or another chart type.
- Do not use 3D, rainbow palettes, radial bars, radar charts, or pie/donut charts by default for business/reporting assets.

## Chart standards

- Use a clear, factual title and subtitle.
- By default, chart text should explain what is plotted, not interpret what it means.
- Label axes with units, but avoid repeating the same unit in title, subtitle, axis title, and panel labels.
- Prefer a 0 baseline for y-axes, especially for counts, volumes, revenue, rates, proportions, and comparison charts unless there is a strong analytical reason to do otherwise.
- Compact large y-axis tick labels so charts remain readable, such as `250,000` to `250k`, `1,200,000` to `1.2M`, and `3,400,000,000` to `3.4B`.
- Keep axis titles explicit about the metric and units even when tick labels are compacted, such as `Daily active users`, `Revenue (USD)`, or `Tokens`.
- Use date formatting appropriate to the grain.
- Annotate known events, releases, data-quality caveats, or specific values only when they help the reader understand the encoding/context.
- Include source/model and caveat note in a caption or adjacent text.
- Prefer consistent, restrained colors over default rainbow palettes.
- Save chart files locally and report their absolute paths.

Factual chart text policy:

- Do not use interpretive/takeaway headlines by default. Avoid titles such as "X dominates," "Y collapsed," "A drives B," "Z is recovering," or "conversion is weak" unless the user explicitly asks for a takeaway chart or presentation narrative.
- Default title pattern: `<metric> by <dimension/grouping>` or `<metric> over time by <grouping>`.
  - Good: `Daily orders by region`
  - Good: `Revenue by plan and product`
  - Avoid by default: `Mobile dominates order volume`
  - Avoid by default: `Enterprise plan drives revenue`
- Use the subtitle/caption for factual context: time window, grain, filters, top-N rule, current-day exclusion, aggregation, and whether values are counts, rates, currency, or percentages.
- Keep interpretive analysis in the surrounding written response, not embedded in the chart, unless requested. The chart should remain reusable as a neutral evidence artifact.
- If a user asks for a slide/report "headline" or "takeaway," still keep claims mechanically checkable: name the metric, comparison basis, population, and time window. Prefer `Top two plans account for 62% of revenue` over `Top two plans drive revenue`.
- Annotations should be factual labels, not conclusions. Prefer `May 13 high` or `Release date` over `backfill spike`, `collapse`, or `recovery` unless that cause is verified.
- Alt text and metadata should be factual descriptions of the chart contents and encodings. Put caveats and interpretation in separate `caveats` or analysis fields.

Title, axis, and legend checklist:

- Title: identifies the plotted metric and primary dimension/grouping; no unexplained conclusion verbs.
- Subtitle: adds time window, grain, filters, and top-N/coverage rules when needed.
- X-axis: labeled unless the tick labels and title/subtitle make the dimension unambiguous, such as obvious calendar years; do not make readers guess.
- Y-axis/value scale: labeled with metric and unit, such as `Orders`, `Revenue (USD)`, `Active users`, or `Share of users (%)`.
- Legend/direct labels: identify what color, line style, marker, or panel represents. Prefer direct labels when they fit; otherwise keep the legend outside the data region and ordered to match the visual order.
- Caption/source note: includes source table/model, freshness/current-day exclusion if relevant, important filters, top-N truncation, and scale caveats such as independent axes or log scale.

Chart integrity rules:

- Bar charts must start their value axis at zero.
- Line charts do not always require a zero baseline, but for report-quality count/volume charts, prefer zero-anchored axes unless there is a clear reason not to. If using a nonzero axis, disclose it or make the design choice obvious.
- When comparing absolute magnitudes across groups, prefer shared axes/scales.
- When the goal is per-series trend readability and one group dwarfs the others, prefer small multiples or indexed trends over a single shared-axis line chart.
- If using independent y-axes in small multiples, make that choice explicit through panel design/context and preserve magnitude context with totals, averages, or summary labels.
- If one series is more than roughly 5-10x larger than the others, do not default to a single multi-line shared-axis chart. Consider small multiples, split panels, indexed trends, or asking whether the user cares about absolute volume or trend shape.

Labeling and annotation rules:

- Prefer direct labels, end labels, or panel titles over legends when practical.
- Keep legends outside the data region and order legend entries to match the chart order.
- Use annotations sparingly to label a known event, data-quality caveat, notable value/outlier, or how to read an uncommon chart. Do not annotate interpretive conclusions by default.
- Do not add reference lines such as means unless they support the question or improve interpretation.

Accessibility/reporting rules:

- Use high-contrast text and avoid relying on color alone when distinctions are important.
- Use plain language in titles, labels, notes, and caveats.
- Keep enough context for the chart to be understood outside the conversation: metric, grain, time window, filters, source, and caveats.

## Visual style

Default to a clean, neutral style that reads well in any report. This skill is brand-agnostic; do not apply any organization's branding unless the user asks.

- Plain HTML/CSS/JavaScript/SVG interactive artifact on a white or off-white background.
- Dark, high-contrast text.
- A clean sans-serif font stack, such as `system-ui`, Inter, or similar.
- A small, restrained, consistent palette (about 4-6 colors); avoid rainbow defaults.
- Title left-aligned when supported.
- Legend above or to the right, not overlapping the data.
- Clear axis labels with units, e.g. `Orders`, `Cost (USD)`, `Active users`.
- Date ticks matched to grain: daily, weekly, or monthly.
- Chart dimensions suitable for reports: about 1000x600 for HTML/static exports unless the user requests otherwise.

If the user or project has its own brand palette and fonts, use those. Otherwise the neutral defaults above are fine. Do not invent "official" brand colors for an organization.

### Optional: Cline brand tokens

A ready-made token set is bundled at `styles/cline-chart-tokens.css` (self-contained CSS custom properties: palette, fonts, backgrounds, and chart dimensions) encoding the Cline web brand ([cline-web](https://github.com/cline/cline-web)). It is entirely optional and provided as one example, use it if you want that look, or swap in your own tokens. If you reference it but cannot load the exact tokens in another environment, say the style is an approximation. Do not add Cline (or any other) branding to charts by default.

## Artifact contract

Every successful plotting run should save the underlying data and the chart locally.

Default artifact location:

```text
artifacts/data-analyst/<descriptive-slug>/
```

Use the current workspace as the base directory. Create the directory if needed. Report absolute paths in the final response.

Preferred outputs:

1. CSV of the underlying plotted data.
2. Plain HTML/CSS/JavaScript/SVG interactive chart for exploratory interactive artifacts.
3. PNG when requested or useful for reports/presentations and static export dependencies are available.
4. Plotly/Vega/ECharts/etc. HTML only when the user asks for that library, the chart needs library-specific features, or custom vanilla SVG would be disproportionately complex.
5. Optional metadata/notes file for report-ready assets.

If the user explicitly asks for a PNG and static export dependencies are unavailable, install them in a local workspace virtual environment when reasonable instead of hand-rolling rasterization. Prefer:

```bash
python3 -m venv .venv-plotting
.venv-plotting/bin/python -m pip install plotly kaleido pandas
```

If dependency installation is impossible, save the CSV and explain what chart would have been generated. Do not create low-quality manual SVG/PNG renderers as a fallback for report assets.

For report-ready assets, consider saving a small sidecar metadata file such as `chart_metadata.json` with:

```json
{
  "title": "...",
  "alt_text": "...",
  "chart_type": "...",
  "data_source": "...",
  "metric": "...",
  "grain": "...",
  "time_window": "...",
  "filters": ["..."],
  "caveats": ["..."],
  "generated_files": ["..."]
}
```

Use this response shape after plotting:

```md
Chart: /absolute/path/chart.html
Data: /absolute/path/data.csv

Mapping:
- chart type: ...
- x: ...
- y: ...
- color/group: ...

Source:
database.model_or_table, query, or artifact path

Caveats:
time window, filters, top-N rule, freshness, exploratory/report-ready status
```

## Recommended implementation

For interactive exploratory charts, prefer a self-contained vanilla artifact:

1. Plain HTML/CSS/JavaScript/SVG with the bounded aggregate data embedded as JSON or CSV.
2. Include the necessary interaction directly in vanilla JS: legend/filter toggles, hover tooltip, click details, metric/view toggles, share vs count normalization, small multiples, etc.
3. Avoid external network/CDN dependencies by default; the artifact should work when opened locally/offline.
4. Keep the chart code simple and inspectable. Do not build a broad dashboard unless the user asks for it.

Use local Python/charting libraries in this order when a static export, report asset, or specialized chart is more appropriate:

1. Matplotlib/seaborn for static PNG/SVG report assets.
2. Plotly PNG export when Plotly/Kaleido are already available or explicitly requested.
3. Plotly/Vega/ECharts/etc. for interactive HTML only when the user asks for that library or vanilla SVG would be a poor fit.
4. CSV output only if plotting is not feasible.

For bounded aggregate analytics data, a self-contained vanilla HTML/CSS/JavaScript/SVG chart is usually the preferred interactive artifact. Prefer this over Plotly-by-default and over low-quality static fallbacks when the user wants exploration and the data volume is small enough to embed safely.

Recommended features for self-contained interactive HTML/SVG charts:

- Embed only aggregate, non-sensitive plotted data.
- Use inline SVG for marks, axes, gridlines, labels, and accessibility text.
- Provide hover and keyboard-focus tooltips for datapoints.
- Include useful controls such as metric selector, y-axis scale selector, label toggle, or segment/highlight toggles only when they aid exploration.
- Include source/caveat captions visible next to the chart.
- Include the underlying data table when practical.
- Provide CSV/SVG download buttons when browser security context allows them.
- Keep the artifact usable offline and avoid external network/CDN dependencies unless the user explicitly wants them.
- Prefer custom SVG marks over canvas when axes, labels, tooltips, legends, and click targets need to remain easy to inspect and modify.
- Add lightweight summary metrics or a details table when they materially improve exploration.

Always keep the underlying data artifact, such as CSV or query output, when generating a chart.

Prefer a small local script or a clearly structured HTML file over ad hoc shell one-liners when generating a chart so the mapping, style, file paths, embedded data, and dependencies are easy to inspect.

Before returning a chart artifact, inspect or validate the rendered output. Reject and fix charts with clipped captions, missing legends, labels running off canvas, unreadable axes, confusing log ticks, misleading baselines, or badly compressed series. If one series dwarfs the rest, consider small multiples, split panels, indexed trends, normalization, or a clearly labeled log scale depending on the analytical intent.

When possible, open or read the actual image artifact before finalizing. Do not rely only on code inspection.

## Interactive HTML validation

Before reporting an interactive HTML artifact as complete:

1. Validate that expected controls, labels, source notes, and embedded data are present in the generated file.
2. If the file contains inline JavaScript, extract `<script>` blocks and run `node --check` when Node is available.
3. Watch for generator escaping bugs, especially literal newlines inside JavaScript string literals, unescaped backticks in template literals, and manually concatenated JSON. Prefer `json.dumps`/equivalent for embedded data.
4. If the artifact is generated by a script, fix the generator and regenerate the artifact. Do not only hand-patch the generated HTML unless the generator is also updated or clearly marked obsolete.
5. For local interactive HTML, note that opening via `file://` can restrict downloads, object URLs, module imports, or other browser features. If relevant, include local serving instructions such as:

```bash
cd /path/to/artifact-directory
python3 -m http.server 8000
```

Then open `http://localhost:8000/chart.html`.

## Smoke-test query for plotting changes

Use a bounded query like this as a basic plotting smoke test against any daily aggregate table you have. Adapt the table and column names to your schema. It should produce a multi-line or small-multiple time-series chart with the date on x, a count metric on y, and a low-cardinality category as the color/group dimension. Save both CSV and a plain HTML/CSS/JavaScript/SVG interactive artifact.

```sql
WITH top_categories AS (
  SELECT category
  FROM analytics.daily_events
  WHERE event_date >= today() - 30
    AND event_date < today()
    AND category IS NOT NULL
    AND category != ''
  GROUP BY category
  ORDER BY sum(event_count) DESC
  LIMIT 5
)
SELECT
  event_date,
  category,
  sum(event_count) AS events,
  uniqExact(user_id) AS active_users,
  round(events / nullIf(active_users, 0), 2) AS events_per_active_user
FROM analytics.daily_events
WHERE event_date >= today() - 30
  AND event_date < today()
  AND category IN (SELECT category FROM top_categories)
GROUP BY event_date, category
ORDER BY event_date, events DESC
```

Expected plot contract for this query:

- chart type: start with a multi-line chart only if the top categories are comparable in magnitude; otherwise prefer small multiples or ask whether the user wants absolute volume or trend-shape comparison
- x: `event_date`
- y: `events`
- color/group: `category`
- source: `analytics.daily_events`
- caveats: last 30 complete days; top 5 categories by total event count
