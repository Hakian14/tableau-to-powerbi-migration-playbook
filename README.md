# Tableau → Power BI Migration Playbook

[![Docs](https://img.shields.io/badge/type-playbook-6E40C9)](#)
[![Power BI](https://img.shields.io/badge/Power%20BI-DAX%20%7C%20Power%20Query-F2C811?logo=powerbi&logoColor=black)](03_calculations/calculated_fields_to_dax.md)
[![Tableau](https://img.shields.io/badge/Tableau-source-E97627?logo=tableau&logoColor=white)](#)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE)

A practical, end-to-end guide for moving reporting from Tableau to Power BI, written from
migrations I ran for SME clients as a freelance analyst. It covers the part the vendor docs skip:
**what breaks, what has no equivalent, how to prove the numbers match, and how to get users to
switch.**

Who it is for: the analyst or small BI team handed "move these 40 dashboards by Q3".

## The playbook in one page

| Phase | Deliverable | Guide | Template |
|---|---|---|---|
| 1. Assess | Workbook inventory with complexity score and migration order | [01_assessment](01_assessment/README.md) | [`inventory.csv`](templates/inventory.csv) |
| 2. Model | Power BI star-schema model replacing Tableau data sources, blends and LODs | [02_data_model](02_data_model/README.md) | — |
| 3. Calculate | Every calculated field re-expressed as a DAX measure | [03_calculations](03_calculations/calculated_fields_to_dax.md) | — |
| 4. Visualise | Report pages mapped visual-by-visual, with the "no equivalent" list resolved | [04_visuals](04_visuals/README.md) | — |
| 5. Optimise | Model and visuals under the performance budget | [05_performance](05_performance/README.md) | — |
| 6. Validate | Signed reconciliation: numbers match, or the difference is explained | [06_validation](06_validation/README.md) | [`test_cases.csv`](templates/test_cases.csv) |
| 7. Roll out | Parallel run, training, decommission | [07_rollout](07_rollout/README.md) | [`migration_checklist.md`](templates/migration_checklist.md) |

## Five things I wish someone had told me before the first migration

1. **Migrate the data model, not the dashboards.** A Tableau workbook with 12 data sources and six
   blends becomes *one* Power BI model with relationships. Rebuilding dashboards 1:1 on top of
   twelve imported tables is the most common and most expensive mistake.
2. **LOD expressions are not calculated columns.** `{FIXED [Customer] : SUM([Sales])}` is a
   `CALCULATE` with `ALLEXCEPT` / `REMOVEFILTERS` measure, evaluated in the visual's filter
   context. Tempting shortcuts (calculated columns, SUMMARIZE tables) give the right number in
   one visual and the wrong one in the next.
3. **Table calculations are the hardest 10%.** `RUNNING_SUM`, `WINDOW_AVG`, `LOOKUP(-1)` and
   `RANK` with "compute using" depend on the visual's layout in Tableau. In Power BI they become
   measures over an explicit date or rank dimension — more work up front, far more robust.
4. **"Matches Tableau" is a test plan, not a feeling.** Before migrating anything, record every KPI
   on every dashboard at three filter states. That table is the acceptance criterion
   ([06_validation](06_validation/README.md)).
5. **Users do not switch because the new report exists.** They switch when the old one is read-only,
   the new one is in their Teams channel, and someone has sat with them for twenty minutes.

## Results from the migrations this is based on

- 40+ dashboards across sales, marketing and operations for retail and e-commerce SMEs
- Typical visual load time from **9–12 s (Tableau extract) to under 2 s** after remodelling
  ([05_performance](05_performance/README.md) lists exactly what moved the needle)
- 100% of KPIs reconciled to the Tableau source at sign-off; the 3–4 differences per project that
  *should* exist (fixed Tableau bugs, changed definitions) documented rather than reproduced

## How to use this repository

Copy the `templates/` into the project's shared folder, work the phases in order, and treat each
guide's checklist as the exit criterion for the phase. The DAX mapping table in
[03_calculations](03_calculations/calculated_fields_to_dax.md) is meant to be kept open while rebuilding.

Related repositories that show the Power BI side in practice:
[omnichannel-retail-powerbi](https://github.com/Hakian14/omnichannel-retail-powerbi) (star schema,
54 DAX measures, performance notes).

## About

Written by **Ha Kieu Anh** — Data Analyst, Microsoft Certified: Data Analyst Associate, 5+ years in
retail, e-commerce and CRM analytics; freelance Tableau → Power BI migrations 2024–2025.
[GitHub](https://github.com/Hakian14) · [LinkedIn](https://www.linkedin.com/in/kieu-anh-ha-6249a3172/) · hakieuanh662@gmail.com

License: [CC BY 4.0](LICENSE) — reuse freely with attribution.
