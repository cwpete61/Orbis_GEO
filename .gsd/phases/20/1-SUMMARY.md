---
phase: 20
plan: 1
wave: 1
status: completed
---

# Plan 20.1: Production Math Hardening Summary

## Work Completed

- **Grid Math Normalization**: Verified that `scripts/gbp_grid.py` properly calculates `potential_score` with proportional improvements capped conceptually by the current score (specifically using `min(current_score, potential_rank)` to not worsen scores).
- **Synchronized Projections**: Implemented consistent projection formulas between `scripts/generate_pdf_report.py` and `dashboard/app.js`. Both now uniformly apply the `expansion_factor` combining `rank_improvement * 2.5` and `fallout_improvement * 0.3`.  
- **Negative Logic Prevention**: Added explicit `max()` and `Math.max()` checks globally in `app.js` and `scripts/generate_pdf_report.py` to ensure `pot_max_reach_mi` is strictly `>=` `maxReachMi`.
- **API Error Handling**: Updated `app.js` `runStep` function to catch `!response.ok` cases (e.g. 500 errors and timeouts), log the `response.status` to the UI terminal, and cleanly exit without breaking the dashboard UI flow.

## Success Criteria Met
- [x] No "Rank 1.0" for businesses with low AI trust scores.
- [x] Dashboard metrics match PDF metrics exactly through mirrored projection logic.
- [x] 500 API/Timeout errors are reliably parsed and appended to the visible browser log.
