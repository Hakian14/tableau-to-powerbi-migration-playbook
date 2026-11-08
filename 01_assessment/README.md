# Phase 1 — Assessment

**Goal:** know what you are migrating before promising a date. Output: a scored inventory and a
migration order the business has agreed to.

## 1. Inventory every workbook

Fill [`templates/inventory.csv`](../templates/inventory.csv), one row per workbook. Pull most of it
from Tableau Server/Cloud (Admin Views, or the REST API / Metadata API for large estates):

| Column | Where to get it | Why it matters |
|---|---|---|
| `workbook`, `project`, `owner` | Server | Owner signs off the migrated version |
| `views_90d`, `distinct_users_90d` | Admin view *Traffic to Views* | Usage drives priority; ~30% of workbooks usually have zero views — candidates for retirement, not migration |
| `data_sources`, `extract_or_live`, `blends` | Workbook XML (`.twb`) or Metadata API | Blends and multiple sources are the model-redesign work |
| `n_sheets`, `n_dashboards` | Workbook | Volume |
| `n_calc_fields`, `n_lod`, `n_table_calcs`, `n_parameters`, `n_sets` | Workbook XML — count `<calculation>` nodes; LODs contain `{`, table calcs contain `WINDOW_`, `RUNNING_`, `LOOKUP`, `RANK`, `INDEX()` | Complexity drivers (see scoring) |
| `custom_sql` | Data source XML | Custom SQL moves to the warehouse or Power Query — extra work and a review |
| `dashboard_actions` | XML `<action>` | Become bookmarks / drill-through — each one is manual |
| `rls` | Server user filters | Row-level security must be rebuilt with roles |
| `refresh_schedule` | Server | Gateway / dataset refresh planning |

A Python snippet that parses a `.twb` for these counts is in [`parse_twb.py`](parse_twb.py).

## 2. Score complexity

Score each workbook 0–3 on six factors and sum (0–18):

| Factor | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Data sources | 1 source, no blends | 2 sources or 1 blend | 3–4 sources / blends | 5+ or custom SQL with logic |
| Calculated fields | < 10 | 10–30 | 31–60 | > 60 |
| LOD expressions | 0 | 1–3 | 4–10 | > 10 or nested LODs |
| Table calculations | 0 | 1–3 simple (RUNNING_SUM) | 4–10 or any "compute using" | nested / addressing across dimensions |
| Interactivity | filters only | parameters | dashboard actions, sets | parameter-driven measure swapping, dynamic zones |
| Security & refresh | public, manual refresh | scheduled refresh | user filters | RLS + live connection + embedding |

| Total | Class | Typical effort (one analyst) |
|---|---|---|
| 0–5 | Simple | 0.5–1 day |
| 6–10 | Medium | 2–4 days |
| 11–14 | Complex | 1–2 weeks |
| 15–18 | Redesign | treat as a new build; reuse requirements only |

Effort assumes the data model (Phase 2) is already in place. The first workbook on a new model
carries the model effort too.

## 3. Decide the order

Three questions, in order:

1. **Retire?** Zero views in 90 days and no owner objection → do not migrate. Record the decision.
2. **Which model does it need?** Group workbooks by the business process (sales, inventory, marketing).
   Migrate one group at a time so the model is built once and reused.
3. **Quick win first.** Within the first group, start with a *medium* workbook that has a vocal
   owner — simple enough to finish in a week, visible enough to build confidence.

## 4. Record definitions now

For every KPI on every dashboard, write down the **definition as the business understands it**
(not the Tableau formula). Half of the "numbers don't match" conversations in Phase 6 are
definition disagreements that already existed in Tableau. Finding them now turns them into scope,
not surprises.

## Exit checklist

- [ ] Inventory complete; every workbook has owner, usage, complexity score, decision (migrate / retire / redesign)
- [ ] Workbooks grouped by target data model
- [ ] KPI definitions recorded for the first group
- [ ] Migration order and dates agreed with owners
- [ ] Environment ready: Power BI workspace, gateway (if on-prem), source access, naming convention
