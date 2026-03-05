---
phase: 17
plan: 3
wave: 3
---

# Phase 17 - Wave 3: PDF Simulation Block

## <task> Incorporate Simulation Data into PDF Report
1. Review `scripts/generate_live_pdf.py` to understand how the report renders blocks.
2. Add a new full-page "Simulation Comparison" block to the PDF generation logic.
3. This block should display the Base vs. Optimized Map or the comparative grid points, similar to the dashboard.

## <verify>
- Run the full audit workflow (or a test script calling `generate_live_pdf.py`) and confirm that the final `.pdf` output includes the new Simulation section.
