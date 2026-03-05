---
phase: 19
plan: 1
wave: 1
---

# Phase 19: Aggressive GEO Expansion Sync - Plan 1

## Goal
Synchronize the Case Studio dashboard module with the new Aggressive GEO Expansion math and Local Visibility terminology used in the main dashboard and PDF report.

<task>
1.  **Update Case Studio UI Labels**
    *   File: `dashboard/case-studio.html`
    *   Find the "Avg. Rank (Current)" and "Avg. Rank (Potential)" labels in the `.brand-header` sections.
    *   Change them to "Local Visibility (Current)" and "Local Visibility (Potential)".
    *   Find "Avg Rank (Current)" and "Avg Rank (Optimized)" in the grid stats render area and change to Local Visibility.
</task>

<task>
2.  **Update Case Studio Math Engine**
    *   File: `dashboard/case-studio.html` (in the `<script>` tag)
    *   Modify the `renderStats` and `runSimulation` functions to calculate and display the *center point rank* instead of the calculated mathematical average.
    *   Apply the same `minDist` logic used in `app.js` to find the grid point closest to the target coordinates.
</task>

<verify>
```bash
# Verify the HTML file string replacements
grep "Local Visibility" dashboard/case-studio.html
# Verify JS math changes
grep "centerRank" dashboard/case-studio.html
```
</verify>
