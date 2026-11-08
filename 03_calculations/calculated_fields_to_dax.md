# Phase 3 — Calculated fields → DAX

**Goal:** every Tableau calculation has a DAX equivalent that returns the same number in the same
filter context, as a **measure** unless there is a reason for a column.

## First rule: measure or column?

| Tableau calc behaves like… | Power BI |
|---|---|
| Row-level (`[Price] * [Qty]`, string cleanup, bucketing) | **Calculated column** — better still, a Power Query step |
| Aggregate (`SUM(...) / SUM(...)`, anything with `AGG`) | **Measure** |
| LOD | **Measure** with `CALCULATE` and filter modifiers |
| Table calculation | **Measure** over an explicit dimension (`dim_date`, rank) |

Tableau lets a field be both; Power BI makes you choose. Choosing measure almost always makes the
result correct in more places.

## Core function mapping

| Tableau | DAX | Notes |
|---|---|---|
| `SUM([x])`, `AVG`, `MIN`, `MAX`, `COUNT`, `COUNTD` | `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNT`/`COUNTROWS`, `DISTINCTCOUNT` | `COUNT` in Tableau counts non-null; use `COUNT(col)` or `COUNTROWS` accordingly |
| `SUM([Sales]) / SUM([Qty])` | `DIVIDE ( SUM ( f[sales] ), SUM ( f[qty] ) )` | Always `DIVIDE`; it handles zero |
| `ZN([x])` | `COALESCE ( [x], 0 )` or `[x] + 0` | Prefer leaving BLANK in measures; show "0" via format string if needed |
| `IF c THEN a ELSEIF d THEN b ELSE e END` | `SWITCH ( TRUE (), c, a, d, b, e )` | `IF` for two branches |
| `CASE [f] WHEN 'a' THEN 1 WHEN 'b' THEN 2 END` | `SWITCH ( [f], "a", 1, "b", 2 )` | |
| `IIF(c, a, b)` | `IF ( c, a, b )` | |
| `ISNULL([x])` / `IFNULL([x], y)` | `ISBLANK ( [x] )` / `IF ( ISBLANK ( [x] ), y, [x] )` | |
| `DATEDIFF('day', a, b)` | `DATEDIFF ( a, b, DAY )` | Same name, argument order differs |
| `DATETRUNC('month', d)` | `DATE ( YEAR ( d ), MONTH ( d ), 1 )` or `EOMONTH ( d, -1 ) + 1` | Or use `dim_date[month_start]` |
| `DATEADD('month', 1, d)` | `EDATE ( d, 1 )`; for days `d + 1` | |
| `DATEPART('weekday', d)` | `WEEKDAY ( d, 2 )` | Check the return-type argument (1 = Sun-first, 2 = Mon-first) |
| `TODAY()`, `NOW()` | `TODAY ()`, `NOW ()` | Measures recalculate on refresh / query, not continuously |
| `LEFT`, `RIGHT`, `MID`, `LEN`, `UPPER`, `LOWER`, `TRIM` | Same names (`MID` is 1-based in both) | |
| `CONTAINS(s, sub)` | `CONTAINSSTRING ( s, sub )` | Case-insensitive in both |
| `SPLIT(s, '-', 2)` | `PATHITEM ( SUBSTITUTE ( s, "-", "\|" ), 2 )` or Power Query *Split column* | Prefer Power Query |
| `STR([x])`, `INT`, `FLOAT` | `FORMAT`, `INT`, `VALUE` | |
| `REGEXP_*` | No native regex in DAX → Power Query (`Text.*`) or upstream | |
| `ATTR([x])` | `SELECTEDVALUE ( t[x] )` or `IF ( HASONEVALUE ( t[x] ), MAX ( t[x] ) )` | Returns BLANK (not `*`) when multiple |
| `[Parameter]` | `SELECTEDVALUE ( Param[Value], default )` | What-if table or disconnected slicer table |
| `USERNAME()` | `USERPRINCIPALNAME ()` | In RLS filter expressions |

## Level-of-detail expressions

The Tableau LOD runs *before* the visual's aggregation at the specified grain. In DAX the
equivalent is a measure whose filter context is modified with `CALCULATE`, or an iterator over the
grain with `*X` functions.

| Tableau | DAX measure | Reading |
|---|---|---|
| `{FIXED [Customer] : SUM([Sales])}` | `CALCULATE ( [Sales], ALLEXCEPT ( f, dim_customer[customer_key] ) )` | Keep only the customer filter. Equivalent: `REMOVEFILTERS ()` + `VALUES ( dim_customer[customer_key] )` when the fact has other dimensions |
| `{FIXED : SUM([Sales])}` (grand total) | `CALCULATE ( [Sales], REMOVEFILTERS () )` | For *share of total*: `DIVIDE ( [Sales], CALCULATE ( [Sales], REMOVEFILTERS ( dim_product ) ) )` — remove only the dimension being compared |
| `{FIXED [Year] : SUM([Sales])}` with a year filter on the view | `CALCULATE ( [Sales], ALLEXCEPT ( f, dim_date[year] ) )` | Tableau FIXED ignores dimension filters but respects context filters; DAX respects whatever you keep — be explicit |
| `{INCLUDE [Store] : AVG([Sales])}` then `AVG` in the view | `AVERAGEX ( VALUES ( dim_store[store_key] ), [Sales] )` | Average of per-store totals at the visual's grain |
| `{EXCLUDE [Region] : SUM([Sales])}` | `CALCULATE ( [Sales], REMOVEFILTERS ( dim_store[region] ) )` | |
| `COUNTD({FIXED [Customer] : MIN([Order Date])})` — new customers | `COUNTROWS ( FILTER ( VALUES ( dim_customer[customer_key] ), CALCULATE ( MIN ( f[order_date] ), REMOVEFILTERS ( dim_date ) ) IN VALUES ( dim_date[date] ) ) )` | Or precompute `first_order_date` on the dimension (Phase 2) and the measure becomes a simple count |
| Nested LOD `{FIXED [Cust] : SUM({FIXED [Cust],[Order] : MAX([Qty])})}` | `SUMX ( VALUES ( f[order_id] ), CALCULATE ( MAX ( f[qty] ) ) )` inside `ALLEXCEPT` on customer | Iterate the inner grain, aggregate the outer |

**Validation tip:** build a matrix with the LOD's dimension on rows and both the migrated measure
and a raw `SUM` side by side; the FIXED measure must not change when you add other dimensions.

## Table calculations

Tableau table calcs depend on the visual's layout ("compute using"). Rebuild them as measures that
name the dimension explicitly, so they work in any visual.

| Tableau | DAX measure | Notes |
|---|---|---|
| `RUNNING_SUM(SUM([Sales]))` along date | `CALCULATE ( [Sales], FILTER ( ALLSELECTED ( dim_date[date] ), dim_date[date] <= MAX ( dim_date[date] ) ) )` | `ALLSELECTED` respects slicers; use `ALL` for from-the-beginning |
| `RUNNING_SUM` restarting each year | `TOTALYTD ( [Sales], dim_date[date] )` | Fiscal year: `TOTALYTD ( ..., "06-30" )` |
| `WINDOW_AVG(SUM([Sales]), -2, 0)` (3-period moving average) | `AVERAGEX ( DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -3, MONTH ), [Sales] )` | Choose the period that matches the visual's grain |
| `LOOKUP(SUM([Sales]), -1)` (previous period) | `CALCULATE ( [Sales], PREVIOUSMONTH ( dim_date[date] ) )` or `DATEADD ( dim_date[date], -1, MONTH )` | `SAMEPERIODLASTYEAR` for LY |
| `(SUM([Sales]) - LOOKUP(SUM([Sales]), -1)) / ABS(LOOKUP(...))` | `DIVIDE ( [Sales] - [Sales PM], ABS ( [Sales PM] ) )` | |
| `RANK(SUM([Sales]), 'desc')` across products | `RANKX ( ALLSELECTED ( dim_product[product] ), [Sales], , DESC, DENSE )` | `ALLSELECTED` so slicers re-rank; `ALL` for a global rank |
| `INDEX()` | `RANKX ( ALLSELECTED ( dim[col] ), CALCULATE ( MAX ( dim[sort_col] ) ), , ASC )` | Usually a sign the visual needs a sort column instead |
| `TOTAL(SUM([Sales]))` | `CALCULATE ( [Sales], ALLSELECTED () )` | Visual total |
| `SUM([Sales]) / TOTAL(SUM([Sales]))` (percent of total) | `DIVIDE ( [Sales], CALCULATE ( [Sales], ALLSELECTED ( dim_product ) ) )` | Remove exactly the dimension being compared |
| `FIRST()`, `LAST()` | `MIN`/`MAX` over `ALLSELECTED ( dim_date[date] )` with `CALCULATE` | |
| `WINDOW_MAX(SUM([Sales]))` highlight | `MAXX ( ALLSELECTED ( dim_date[month] ), [Sales] )` then compare in a conditional-format measure | |

## Parameters

| Tableau parameter use | Power BI |
|---|---|
| Numeric what-if (growth %, discount) | *Modeling → New parameter* (what-if) → `SELECTEDVALUE ( 'Growth %'[Value], 0 )` |
| Measure swap ("show Sales / Profit / Units") | Field parameter (`Modeling → New parameter → Fields`) — native, no DAX |
| Dimension swap | Field parameter |
| Top N | What-if parameter + `TOPN ( SELECTEDVALUE ( 'N'[Value] ), ALLSELECTED ( dim_product ), [Sales] )` as a filter measure |
| Date anchor ("as of") | Disconnected date slicer + `SELECTEDVALUE` → measures use `TREATAS` or `FILTER` on `dim_date` |

## Things that should *not* be translated literally

- **`ATTR()` returning `*`** — in Tableau this hides a grain problem; in Power BI the measure
  returns BLANK. Fix the grain.
- **Calculations referencing sheet-specific "compute using"** — rebuild as explicit-dimension measures above.
- **`ZN()` everywhere** — Tableau needs it for table calcs over sparse data; Power BI measures
  returning BLANK are usually correct and faster (blank rows are not materialised).
- **Date logic on string fields** — fix the type in Power Query.
- **Calculated fields that only exist to fix a join** — fix the model (Phase 2).

## Working method

1. Export the calculated fields list (`.twb` → `<calculation>` nodes; `parse_twb.py` counts them).
2. Classify each: row-level → Power Query; aggregate → measure; LOD/table calc → measure with notes.
3. Write the DAX in `_Measures` with a comment line containing the original Tableau formula —
   it makes validation (Phase 6) a one-screen comparison.
4. Validate each LOD/table-calc measure in a matrix with at least two different dimension layouts.

## Exit checklist

- [ ] Every calculated field classified and either migrated, moved to Power Query, or marked obsolete with a reason
- [ ] Measures carry their Tableau origin as a comment
- [ ] LOD and table-calc measures validated in two layouts each
- [ ] No calculated column on a fact table without a written reason
