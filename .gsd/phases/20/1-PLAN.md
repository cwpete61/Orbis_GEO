---
phase: 20
plan: 1
wave: 1
---

# Plan 20.1: Production Math Hardening

## Objective
Ensure the dashboard and PDF reports use identical, realistic math formulas for visibility, fallout, and reach, especially preventing the "automatic rank #1" bug.

## Context
- .gsd/ROADMAP.md
- scripts/gbp_grid.py
- scripts/generate_pdf_report.py
- dashboard/app.js

## Tasks

<task type="auto">
  <name>Finalize Grid Math Normalization</name>
  <files>
    - scripts/gbp_grid.py
  </files>
  <action>
    - [x] (Already applied) Offset best_possible_rank based on base_score_0_100.
    - Ensure potential_score improvement is proportional but capped at current_score.
  </action>
  <verify>python scripts/gbp_grid.py "Test Brand" 50</verify>
  <done>JSON output shows scores > 1 for low base scores at center point.</done>
</task>

<task type="auto">
  <name>Sync PDF and Dashboard Projection Formulas</name>
  <files>
    - scripts/generate_pdf_report.py
    - dashboard/app.js
  </files>
  <action>
    - Verify that KM_TO_MI (0.621371) is used consistently.
    - Ensure the expansion factors (2.5 for rank, 0.3 for fallout) are applied exactly the same.
    - Add a check for base_pot_reach_mi vs max_reach_mi to prevent negative logic.
  </action>
  <verify>Compare output of dashboard metric calculation to generate_pdf_report.py logic blocks.</verify>
  <done>Formulas match exactly across both languages.</done>
</task>

## Success Criteria
- [ ] No "Rank 1.0" for businesses with low AI trust scores.
- [ ] Dashboard metrics match PDF metrics within +/- 0.1 decimal point.
- [ ] All 500 API errors are caught and reported in the UI terminal log.
