# Phase 5 — Performance

**Goal:** every page under a stated budget. Mine: **≤ 2 s** for any visual on the executive page,
**≤ 4 s** elsewhere, measured with Performance Analyzer on the production model, cold cache.

Tableau users accept slow dashboards they are used to; they do not accept a slow *new* one. The
migration is judged on speed as much as on correctness.

## In the order that moved the needle for me

Numbers are from a retail migration (sales fact ~20M rows, 60 measures, 8 pages). Before: 9–12 s
per visual on the executive page. After: < 2 s.

| # | Change | Effect | Why |
|---|---|---|---|
| 1 | **Flatten the snowflake into a star** (product hierarchy was 4 tables → 1 `dim_product`) | ~35% faster | Every extra relationship hop is a join the engine does per query |
| 2 | **Remove bi-directional relationships** (there were 6, added "so the slicers work") | ~25% faster, and fixed two wrong totals | Bi-di makes the engine evaluate filters in both directions for every query; replaced with `CROSSFILTER` in 2 measures and a bridge table |
| 3 | **Replace `FILTER(ALL(fact), ...)` patterns** with dimension filters in `CALCULATE` | 3 measures went from seconds to ms | Iterating a 20M-row fact to apply a filter that belongs on a 15-row dimension |
| 4 | **Pre-aggregate the footfall sensor feed** at store-day upstream (was 40M pings) | model −30% size | Grain the model needs, not the grain the sensor emits |
| 5 | **Auto date/time off**, one `dim_date` | −15% model size | Hidden date tables per date column |
| 6 | **Aggregation table** (store × month) for the executive page | exec page ~5× faster | Five KPI cards hit a 5k-row table instead of 20M rows |
| 7 | Remove unused columns (IDs, free text, GUIDs) | −20% size | Columns cost memory even unused; high-cardinality text is the worst |
| 8 | Integer surrogate keys instead of text keys | −10% size, faster joins | |
| 9 | Variables in measures; `DIVIDE`; no `IFERROR` | consistent ms gains | Evaluate once; avoid error-handling paths |
| 10 | Visual-level: fewer visuals per page, Top N on tables, no high-cardinality legends | perceived load | Each visual is at least one query |

## Checklist to run before publishing

**Model**
- [ ] Star schema; single-direction relationships; no bi-di without a written reason
- [ ] Auto date/time off; `dim_date` marked
- [ ] No high-cardinality columns that are not needed (`DAX Studio → View Metrics` to find them)
- [ ] Keys are integers; facts have no text columns except what is displayed
- [ ] Semi-additive measures (inventory, balances) use `LASTNONBLANK` / snapshot logic, not `SUM`
- [ ] Consider aggregations when the fact is > 10M rows and the executive page aggregates everything

**DAX**
- [ ] `CALCULATE` with dimension filters, not `FILTER` over facts
- [ ] `ALLSELECTED` vs `ALL` chosen deliberately; no `ALL ( fact )`
- [ ] Iterators (`SUMX`, `AVERAGEX`) over dimensions or `VALUES`, not over the fact unless necessary
- [ ] Time intelligence on `dim_date[date]` only
- [ ] Measures reference base measures (`[Net Sales]`), never re-implement `SUM`

**Visuals**
- [ ] Performance Analyzer run on every page; slowest visual noted and under budget
- [ ] Tables and matrices have a default filter or Top N
- [ ] No visual with > 10 series in the legend
- [ ] Cross-highlighting switched to filter where it caused re-query storms
- [ ] Slicers: no "between" slicers on high-cardinality text; date slicers on `dim_date`

**DirectQuery (if used)**
- [ ] Assume Referential Integrity set on relationships
- [ ] Source has indexes on join keys and filter columns
- [ ] Measures avoid functions that prevent query folding (see the DAX function reference for DQ limitations)
- [ ] Composite model: dimensions in import, large fact in DQ, aggregations in import

## Diagnosing a slow visual (10 minutes)

1. Performance Analyzer → copy the DAX query of the slow visual.
2. DAX Studio → run with *Server Timings*: is it **SE** (storage engine — scan size, model shape)
   or **FE** (formula engine — the DAX itself)?
3. SE-heavy → model problem: cardinality, relationship direction, missing aggregation.
4. FE-heavy → DAX problem: iterator over the fact, `FILTER(ALL(...))`, nested `CALCULATE` with context transition in a loop.
5. Fix one thing, re-measure. Keep the before/after in the validation log — it is part of the sign-off story.

## What to tell the business

Report speed in user terms: "the sales page opens in under two seconds; the Tableau version took
ten." Keep the Performance Analyzer exports as evidence. Speed is the single most persuasive
argument during rollout (Phase 7).
