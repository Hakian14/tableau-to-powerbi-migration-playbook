# Phase 6 — Validation and reconciliation

**Goal:** a signed statement that every KPI on every migrated dashboard matches Tableau, or that
the difference is understood, documented and accepted. This is what makes the migration *done*.

## The test matrix

Build it *before* migrating (Phase 1 records the KPIs; this phase records their values). One row
per KPI × filter state in [`templates/test_cases.csv`](../templates/test_cases.csv):

| Column | Content |
|---|---|
| `dashboard`, `kpi` | What is being checked |
| `filter_state` | `none` · `single` (one typical slicer selection) · `edge` (a boundary: last month with partial data, a store that opened mid-period, a region with no sales) |
| `tableau_value` | Read from Tableau on the frozen reference date |
| `powerbi_value` | Read from Power BI on the same data |
| `tolerance` | Usually 0 for counts and sums; 0.1 pt for percentages shown with one decimal |
| `status` | `match` · `explained` · `open` |
| `explanation` | Required when not `match` |

Three filter states per KPI is the minimum. "No filter" alone passes measures that break the
moment a slicer is used — which is the whole LOD/table-calc problem.

## Freeze the data

Both tools must read the **same snapshot**. Options, best first:

1. Point both at a frozen warehouse table / dated view (`sales_asof_2025_10_31`).
2. Refresh the Tableau extract and the Power BI dataset within the same hour and record both refresh timestamps.
3. Export the Tableau underlying data for the dashboard and load the CSV into Power BI as a one-off validation source.

If the snapshots are not identical, every mismatch becomes an argument about timing. Freeze first.

## Reconciliation procedure

1. **Row counts** — model table rows vs source table rows, per table. Catches filters, joins and duplicates before anything else.
2. **Grand totals** — the top-line number of each fact table with no filters (`Net Sales`, `Orders`, `Units`). Must be exact.
3. **One-dimension splits** — totals by date month, by store, by category. Catches relationship direction and missing keys (blank row appearing = orphan keys).
4. **KPIs at the three filter states** — the test matrix.
5. **LOD / table-calc measures in two layouts** — the same measure in a matrix by product and by store must be internally consistent (shares sum to 100%, running totals end at the grand total).
6. **Edge cases** — leap day, fiscal year boundary, store opening mid-month, returns making a negative day, future-dated records.

## When the numbers differ

Classify every mismatch; the classification *is* the deliverable:

| Class | Example | Action |
|---|---|---|
| **Migration bug** | Measure uses `ALL` where `ALLSELECTED` was needed; relationship missing | Fix, re-test |
| **Tableau bug, now fixed** | Tableau blend double-counted returns; COUNT vs COUNTD | Document; business confirms the new number is right; add to release notes |
| **Definition change** | "Active customer" was 60 days in one sheet and 90 in another | Business picks one; both reports change; log the decision |
| **Snapshot timing** | Refresh gap | Re-freeze and re-test |
| **Rounding / display** | Tableau shows 12.3%, Power BI 12.35% | Align format strings; no model change |

Target at sign-off: **0 open**, every non-match `explained` with a one-line reason and a name.

## Automate the boring part

For large estates, export Tableau values with the REST API (`/views/{id}/data`) and query the
Power BI dataset with the *Execute Queries* REST API (DAX). A notebook that joins the two outputs
on `kpi` + `filter_state` and highlights deltas beyond tolerance turns a week of eyeballing into
an afternoon. For 5–10 dashboards, the spreadsheet is faster than building the harness.

## Sign-off

A one-page note per dashboard group:

- Snapshot date and refresh timestamps (both tools)
- Test matrix summary: *n* KPIs × 3 states, *n* match, *n* explained (listed), 0 open
- Performance: slowest visual before/after
- Known differences the business accepted, with names and dates
- Signature from the dashboard owner

Keep these; they are the answer to "why does this number differ from the old report?" six months later.

## Exit checklist

- [ ] Data frozen; both refresh timestamps recorded
- [ ] Row counts and grand totals exact
- [ ] Test matrix complete at three filter states per KPI
- [ ] Every mismatch classified; 0 open
- [ ] Sign-off note stored with the project documentation
