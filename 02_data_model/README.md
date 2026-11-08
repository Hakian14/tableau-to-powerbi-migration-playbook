# Phase 2 — Data model

**Goal:** one Power BI semantic model per business process that every migrated report shares.
This is where most of the effort goes and most of the value comes from.

## Concept mapping

| Tableau | Power BI | Notes |
|---|---|---|
| Data source (extract) | Import-mode tables | Default choice. Power BI's VertiPaq compresses better than Hyper for typical star schemas. |
| Data source (live) | DirectQuery | Only when freshness is minutes, not hours. Expect 3–10× slower visuals; see Phase 5. |
| Published data source | Shared semantic model (dataset) in a workspace | Reports connect live to the model — same reuse pattern. |
| Joins inside a data source | Relationships in the model (or a Power Query merge when the result is one logical table) | Prefer relationships: fact tables stay thin and filters flow. |
| **Blend** (primary/secondary source on a linking field) | Relationship through a shared dimension | Blends are the #1 reason Tableau workbooks are slow and the #1 modelling win in migration. Each linking field becomes a conformed dimension. |
| Data source filters | Power Query filter steps (import) or RLS (security) | Decide which it was: performance filter → Power Query; security filter → RLS roles. |
| Extract filters / aggregation to visible dimensions | Power Query (or an aggregation table) | |
| Hierarchies | Hierarchies on the dimension table | Same idea; build them on `dim_*` tables, not facts. |
| Groups | Mapping table or Power Query conditional column | Mapping table if the business maintains it. |
| Sets (fixed) | Calculated column `IN {...}` or a flag column from Power Query | |
| Sets (computed / top N) | Measure with `TOPN` / `RANKX`, or a disconnected parameter table | Computed sets are measures, not columns — they depend on filter context. |
| Bins | Calculated column with `SWITCH(TRUE(), ...)` or Power Query bucket | |
| Parameters | What-if parameter (numeric) or disconnected slicer table + `SELECTEDVALUE` (text) | |
| Aliases | Rename in Power Query or a lookup table | |
| Default date properties (fiscal year start) | `dim_date` columns (fiscal_year, fiscal_quarter) | Build a real date table; mark it as date table; turn Auto date/time off. |
| User filters (RLS) | Roles + `USERPRINCIPALNAME()` in RLS DAX, or a security table | Test with *View as role*. |

## Target shape: a star

```
                dim_date
                   │
dim_customer ── fact_sales ── dim_product
                   │
                dim_store
```

- One fact per business event grain (sales lines, inventory snapshots, targets). Do not union
  facts of different grain into one table because Tableau had them in one sheet.
- Dimensions carry every descriptive attribute; facts carry keys and numbers.
- Relationships: one-to-many, single direction, dimension → fact. Bi-directional only as a
  last resort with a written reason.

## The LOD problem, solved at the model level

Tableau LODs often exist because the data source was at the wrong grain. Before translating an
LOD to DAX (Phase 3), ask whether the model should supply the number instead:

| Tableau LOD pattern | Model-level answer |
|---|---|
| `{FIXED [Order ID] : SUM([Qty])}` to de-duplicate line-level joins | Fix the join: keep `fact_sales` at line grain and put order attributes on an `dim_order` or on the header fact |
| `{FIXED [Customer] : MIN([Order Date])}` (first purchase) | A `first_order_date` column on `dim_customer`, computed in Power Query / warehouse |
| `{FIXED [Date] : SUM([Target])}` to bring targets onto daily grain | A separate `fact_targets` at its own grain related through `dim_date` / `dim_month` |
| `{INCLUDE [Store] : AVG(...)}` for average-of-averages | A measure with `AVERAGEX(VALUES(dim_store[store]), [Measure])` — this one stays DAX |

Half of the LODs disappear when the model is right. The rest become measures (Phase 3).

## Power Query vs. upstream

| Do it in Power Query when… | Do it upstream (warehouse / view) when… |
|---|---|
| The source is a file or a system you do not control | The transformation is needed by more than one model |
| Logic is light (types, renames, simple filters, unpivot) | Logic is heavy (de-duplication, SCD, identity resolution) |
| Refresh volume is small (< a few million rows) | Refresh time matters or incremental refresh is needed |

Query folding: keep steps foldable (filter, select, rename, join on keys) early; non-foldable
steps (custom functions, index columns) last.

## Naming conventions (decide once)

- Tables: `dim_*`, `fact_*`, `bridge_*`, `_Measures`.
- Columns: business names in Title Case for anything visible; keys hidden.
- Measures: Title Case, units in the name for ratios (`Gross Margin %`), LY/YoY/MTD/YTD abbreviations only.
- Display folders by business area; numbered so they sort.

## Exit checklist

- [ ] Every Tableau data source and blend in the group is accounted for in the model
- [ ] Star schema drawn and reviewed; grains documented
- [ ] `dim_date` built and marked; Auto date/time off
- [ ] Relationships single-direction; any exception documented
- [ ] RLS roles created and tested if user filters existed
- [ ] Refresh configured (gateway, schedule, credentials) and succeeding
- [ ] Model row counts reconcile to source counts (the first validation step)
