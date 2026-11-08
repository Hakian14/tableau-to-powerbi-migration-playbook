# Phase 7 — Rollout and decommission

**Goal:** the business uses Power BI and nobody opens Tableau. Technically the easiest phase;
in practice where migrations stall.

## Parallel run (2–4 weeks)

- Both reports live; Power BI is the one shared in meetings. Tableau is read-only (no new
  workbooks, no edits) from day one of the parallel run.
- A pinned message in the team's channel: link to the new report, what changed, who to ask.
- Weekly 15-minute check-in with each dashboard owner: what did they look for and not find?
  Fix small things immediately — a missing tooltip field costs an hour and buys trust.
- Track usage in the Power BI workspace usage metrics report. Target before switch-off: Power BI
  views ≥ Tableau views for two consecutive weeks.

## Training that works

- **Twenty minutes, one-to-one or in groups of three**, on the user's own questions — not a
  feature tour. Open the report, ask "what do you look at on Monday morning?", and do that together.
- A one-page "where did it go?" sheet per dashboard: Tableau sheet name → Power BI page and visual,
  including the three or four interactions that changed (right-click → drill through; slicer panel).
- Short screen recordings (under 2 minutes) for the three most common tasks: filter to my region,
  export to Excel, subscribe.
- Power users: a 45-minute session on the semantic model so they can build their own reports
  instead of asking for Tableau back.

## Subscriptions and alerts

Recreate every Tableau subscription as a Power BI subscription (per page, per user) and every
Tableau data-driven alert as a Power BI alert on a card/KPI visual or a Power Automate flow.
Users who used to get the email will notice the day it stops — do this before switch-off, not after.

## Security and governance

- Workspace roles: viewers get *Viewer*; analysts who build on the model get *Contributor* on a
  separate reporting workspace; the model lives in a workspace with build permission managed.
- RLS roles tested with every user type (*View as role*) and signed off by the data owner.
- Sensitivity labels applied if the tenant uses them.
- Endorsement: mark the shared semantic model as *Certified* once validation (Phase 6) is signed.
- Naming: workspace, report and page names match the Tableau project/workbook names users know,
  with a "(legacy)" suffix on the Tableau side during parallel run.

## Decommission

After the usage target is met:

1. Announce the switch-off date two weeks ahead, twice.
2. Replace each Tableau dashboard with a single sheet containing the Power BI link (users who
   follow old bookmarks land on the redirect, not on a 404).
3. Archive workbooks (download `.twbx`, store with the sign-off notes) and remove them from Server.
4. Reclaim licences; record the saving — it is usually the business case for the next migration.
5. Thirty days later, delete the redirect workbooks.

## Measuring success

| Metric | Target |
|---|---|
| KPIs reconciled | 100% match or explained, 0 open |
| Slowest visual on key pages | under budget (Phase 5) |
| Weekly active viewers (Power BI vs Tableau baseline) | ≥ 100% of baseline by week 4 |
| Support tickets about "where is X" | trending to zero by week 3 |
| Tableau licences released | 100% of migrated users |

## Exit checklist

- [ ] Parallel run complete; usage target met two weeks running
- [ ] Subscriptions and alerts recreated
- [ ] Training delivered; "where did it go?" sheets published
- [ ] RLS signed off; model certified
- [ ] Tableau workbooks replaced by redirects, then archived
- [ ] Licences reclaimed; savings recorded
- [ ] Project documentation (inventory, test matrices, sign-offs, release notes) stored in the shared folder
