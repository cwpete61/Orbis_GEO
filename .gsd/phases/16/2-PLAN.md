---
phase: 16
plan: 2
wave: 2
---

# Phase 16 - Wave 2: Simulation Integration

## <task> Generate Automated Simulation Report for LightBox SEO
1. Run `python scripts/sim_engine.py "LightBox SEO" 40.6030 -75.4740 65` and save the output.
2. Review `dashboard/case-studio.html` to analyze how Case Studio data flow works.
3. Integrate the simulation engine output into the Case Studio (or log it as completed if it only requires the backend engine for now).

## <verify>
- Check that the `sim_engine.py` execution is successful.
- Verify that the simulation results output provides a measurable delta between baseline and optimized.
