# Migration checklist — <dashboard group>

Owner: · Target date: · Model: · Power BI workspace:

## Phase 1 — Assess
- [ ] Inventory rows complete for every workbook in the group
- [ ] Complexity scored; retire / migrate / redesign decided
- [ ] KPI definitions recorded (business language)
- [ ] Order and dates agreed with owners

## Phase 2 — Model
- [ ] Star schema drawn and reviewed; grains documented
- [ ] All data sources and blends accounted for
- [ ] dim_date built and marked; Auto date/time off
- [ ] Relationships single-direction (exceptions documented)
- [ ] RLS roles created and tested
- [ ] Refresh configured and green
- [ ] Row counts reconcile to source

## Phase 3 — Calculations
- [ ] Every calculated field classified (Power Query / measure / obsolete)
- [ ] Measures carry Tableau origin as comment
- [ ] LOD and table-calc measures validated in two layouts

## Phase 4 — Visuals
- [ ] Every sheet mapped or dropped with agreement
- [ ] Every action mapped (cross-filter / drill-through / bookmark / button)
- [ ] Theme applied; slicers synced; reset bookmark
- [ ] Mobile layout for leadership pages

## Phase 5 — Performance
- [ ] Performance Analyzer on every page; all visuals under budget
- [ ] Model checklist passed (DAX Studio metrics reviewed)

## Phase 6 — Validation
- [ ] Data frozen; refresh timestamps recorded
- [ ] Test matrix complete (3 filter states per KPI)
- [ ] 0 open mismatches; explained ones listed
- [ ] Sign-off note stored

## Phase 7 — Rollout
- [ ] Parallel run started; Tableau read-only
- [ ] Subscriptions and alerts recreated
- [ ] Training delivered; "where did it go?" sheet published
- [ ] Usage target met two weeks running
- [ ] Tableau redirect → archive → licences reclaimed
