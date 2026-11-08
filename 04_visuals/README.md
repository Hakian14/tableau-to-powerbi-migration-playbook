# Phase 4 — Visuals and interactivity

**Goal:** report pages that answer the same questions as the Tableau dashboards — not pixel copies.
Users accept a different-looking report when every number they used to check is still there and
easier to reach.

## Visual mapping

| Tableau | Power BI | Watch out for |
|---|---|---|
| Bar / stacked bar | Clustered / stacked bar or column | Sort explicitly (Power BI sorts by value by default; Tableau often by dimension) |
| Line, dual-axis line | Line chart; **two charts** for dual axis | Dual-axis charts mislead by construction — pick a common scale, index to a base, or use small multiples. The *Line and clustered column* visual exists; use it only when both series share units |
| Area | Area / stacked area | |
| Text table / crosstab | Matrix | Set *Values on rows* for KPI-style tables; turn off stepped layout for a flat look |
| Highlight table | Matrix with conditional background colour | |
| Heat map | Matrix with conditional colour, or the Heatmap custom visual | |
| Scatter | Scatter | Add the dimension to *Values* (not Legend) to get one dot per member |
| Pie / donut | Donut (≤ 4 slices) or bar | Tableau pies with 10 slices become bars |
| Treemap | Treemap | |
| Filled map / symbol map | Azure Maps / Filled map | Needs geocoding-friendly fields (country/city names, lat-long); check tenant settings allow map visuals |
| Gantt | Gantt custom visual or stacked bar with transparent base | |
| Bullet graph | KPI visual or bar with target line (Analytics pane) | |
| Box plot | Box-and-whisker custom visual | Not native |
| Histogram | Column chart on a binned column (Power Query / calculated column) | |
| Sparklines in a table | Matrix sparklines (native) | |
| Big number (BAN) | Card (new card visual supports multiple values and sub-labels) | |
| Reference lines / bands | Analytics pane (constant, average, percentile lines) | Dynamic reference lines need a measure |
| Forecast / trend line | Analytics pane trend line; forecast on line charts | |
| Tooltip viz (viz-in-tooltip) | Report page tooltip | Build a tooltip page, set *Tooltip* page type |
| Story points | Bookmarks + buttons, or separate pages | |

## Interactivity mapping

| Tableau | Power BI | Notes |
|---|---|---|
| Quick filter (single/multi list) | Slicer (list / dropdown) | Sync across pages: *View → Sync slicers* |
| Relative date filter | Slicer → *Relative date* | |
| Filter action (click bar → filter other sheets) | Default cross-filtering (set *Edit interactions* to Filter rather than Highlight where needed) | Free in Power BI; choose filter vs highlight per visual |
| Highlight action | Default cross-highlight | |
| URL action | Conditional URL on a table column, or button with URL action | |
| Go-to-sheet / drill action | **Drill-through** page (right-click → drill through) or button | Carry filters with *Keep all filters* |
| Parameter control | What-if slicer / field-parameter slicer | |
| Show/hide containers | Bookmarks + buttons, or the native visual-level toggles | |
| Sheet swapping via parameter | Field parameters (metric swap) or bookmarks (layout swap) | |
| Apply-to-worksheets filter scoping | Visual / page / report-level filters in the Filters pane | |
| Context filters | Not needed (Power BI evaluates filters together); watch for performance-driven context filters → model filters instead | |
| Sets as filters / in-out | Slicer on a flag column, or `IN` measure | |

## Features with no direct equivalent — and what to do

| Tableau feature | Resolution |
|---|---|
| Dual axis with synchronised axes and different marks | Two visuals, or *Line and clustered column* only for same-unit series |
| "Compute using" table calcs tied to the visual layout | Explicit-dimension measures (Phase 3) — more robust |
| Dashboard device layouts | Mobile layout view (one layout per report page, portrait only) |
| Data highlighter | Slicer with *single select*, or search in a slicer |
| Pages shelf (animation) | Play axis on scatter (animated scatter only); otherwise a slider slicer |
| Hide/show sheets inside a dashboard dynamically | Bookmarks (manual) or conditional visibility via a measure-driven page-navigator |
| Extract-only features (e.g. `TODAY()` evaluated at extract time) | Measures evaluate at query time — verify "as of" semantics |
| Custom fonts | Only theme-supported fonts; Segoe UI is the safe default |
| Dashboard 1:1 exported as PDF with exact layout | Paginated reports (Power BI Report Builder) for pixel-perfect print |

## Layout principles that stop the "it looks worse" conversation

1. **One question per page.** Tableau dashboards often cram 12 sheets; split them. Users navigate
   by page tab, not by scrolling.
2. **KPI row on top, trend in the middle, detail at the bottom.** Consistent across pages.
3. **Slicers in one place** (left panel or top bar), synced, with a *Reset* bookmark button.
4. **Theme file** for colours, fonts and visual borders so every page looks like one product.
   (Example: [`theme.json` in the retail dashboard repo](https://github.com/Hakian14/omnichannel-retail-powerbi/blob/main/report/theme.json).)
5. **Tooltips carry the detail**, not the page: report-page tooltips replace most Tableau
   viz-in-tooltip and many drill actions.
6. **No more than ~15 visuals per page**, and nothing that renders a table with thousands of
   rows by default — add a slicer with a default selection or a Top N filter.

## Exit checklist

- [ ] Every Tableau sheet mapped to a visual or deliberately dropped (with the owner's agreement)
- [ ] Every dashboard action mapped to cross-filter, drill-through, bookmark or button
- [ ] Theme applied; slicers synced; reset bookmark on every page
- [ ] Mobile layout for the pages leadership opens on phones
- [ ] Each page renders in under the performance budget (Phase 5)
