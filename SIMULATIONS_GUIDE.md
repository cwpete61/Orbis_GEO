# GEO Simulation Guide (2026)

This guide outlines the methodology for conducting advanced **Generative Engine Optimization (GEO)** simulations using the Orbis Local toolset.

## Simulation Framework

### 1. Baseline Performance
- Run a full `/geo-seo-global` audit to capture current visibility scores.
- Export the benchmark PDF for comparison.

### 2. Delta Analysis
- Use the **Case Studio** to compare side-by-side performance against a "Zero-Fee" benchmark.
- Identify the largest "Visibility Gaps" in the GBP grid.

### 3. Optimization Sandbox
- Modify `schema/` and `geo-report/` templates to test hypothetical content changes.
- Re-run `citability_scorer.py` on the optimized content.

## Advanced Techniques

### "Flatter" Rank Distribution
Optimizing for service pages and local GEO signals aims to reduce the "Search Fallout" percentage. 
> Target: Maintain < Rank 5 within a 8km radius (Current average: 5km).

### AI Citation density
Focus on increasing the **Statistical Density** and **Self-Containment** scores in `citability_scorer.py`.
> Target: Average citability score > 75.

## Running Simulations
1. Create a sub-directory in `simulations/[BRAND]/`.
2. Save raw JSON audit data for each iteration.
3. Compare `total_score` changes across versions.
