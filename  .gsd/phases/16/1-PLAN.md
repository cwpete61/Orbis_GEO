---
phase: 16
plan: 1
wave: 1
---

# Phase 16 Plan: Simulation Engine & Logic Foundation

This phase establishes the technical foundation for running algorithmic simulations that predict visibility gains from specific GEO optimizations.

## Tasks

### 1. Simulation Engine Core (Wave 1)
- [ ] Create `scripts/sim_engine.py`.
- [ ] Implement `calculate_visibility_impact` function using the flat-rank decay model.
- [ ] Create `scripts/sim_utils.py` for shared simulation data structures.

### 2. Integration & Generation (Wave 2)
- [ ] Update `dashboard/server.js` to expose a `/api/simulate` endpoint.
- [ ] Generate a baseline simulation for "LightBox SEO" in Allentown.
- [ ] Verify output JSON matches the expectations for the Case Studio.

## Verification
- [ ] Run `python scripts/sim_engine.py` and verify JSON output.
- [ ] Verify the `/api/simulate` endpoint returns success.
