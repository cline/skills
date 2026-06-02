# Data Analyst Example Prompts

Realistic example questions for the data analyst. These are phrased the way a real user might ask: clear enough to start, but often vague enough that the analyst should ask clarifying questions before querying.

Each example names the eventual artifact the user wants, not the exact tables, columns, or SQL to use. That is the point: turn an underspecified ask into a confirmed Intent block first.

---

## 1. Revenue by product line (business health)

Prompt:

> Show me total revenue, cost, and gross margin for the last 30 days, broken down by product line. Include the margin percentage for each, and export the result as a CSV.

Expected artifact: CSV export with revenue, cost, margin, and margin % per product line.

Likely clarifications: gross vs net revenue, which 30-day window (rolling vs completed days), how cost is attributed.

---

## 2. Feature adoption (product quality)

Prompt:

> For the last month, which features do users engage with most? Give me the adoption rate per feature, and tell me which user segment adopts fastest. Plot the results as a bar chart.

Expected artifact: Bar chart showing adoption rate by feature and by segment.

Likely clarifications: definition of "adoption" (any use vs repeated use), which segments, denominator (all users vs active users).

---

## 3. Signup activation funnel (growth)

Prompt:

> I want to understand how users progress after signup. What percentage of users who sign up go on to verify, create their first project, invite a teammate, and become weekly active? Show me the funnel with drop-off at each stage and highlight the biggest gap.

Expected artifact: Funnel report with user counts and conversion rates at each stage, identifying the largest drop-off.

Likely clarifications: cohort window for "signed up," whether stages are ordered/strict, how "weekly active" is defined.

---

## 4. Top errors this week (reliability)

Prompt:

> What are the 10 most frequent errors users are hitting this week? For each, tell me how many distinct users are affected and whether certain platforms or versions are disproportionately impacted. Export as a CSV.

Expected artifact: CSV with top 10 errors, affected user counts, and associated platforms/versions.

Likely clarifications: event count vs unique affected users for ranking, what "this week" means, telemetry coverage caveat.

---

## 5. Session depth and retention (engagement)

Prompt:

> For users who signed up in the last 14 days, what's the 7-day retention rate? Do retained users have longer sessions on average than churned ones? Show me the distribution, maybe a histogram or summary stats, and tell me if the difference looks meaningful.

Expected artifact: Summary statistics comparing session depth for retained vs churned users, with a note on whether the difference is meaningful.

Likely clarifications: retention definition (any return vs active return), session-length metric, whether the sample size supports the comparison.
