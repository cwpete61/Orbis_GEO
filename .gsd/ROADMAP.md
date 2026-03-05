# ROADMAP

## Phase 1: Environment Readiness <!-- id: 0 -->
**Status**: ✅ Complete
- [x] Verify Python 3.8+ installation <!-- id: 1 -->
- [x] Install Claude Code CLI <!-- id: 2 -->
- [x] Install Python dependencies from `requirements.txt` <!-- id: 3 -->
- [x] Install Playwright for screenshot capabilities <!-- id: 4 -->

## Phase 2: Tool Deployment <!-- id: 5 -->
**Status**: ✅ Complete
- [x] Manually map and copy `geo-seo-claude` skills to the Claude Code configuration directory (`%USERPROFILE%\.claude\skills`) <!-- id: 6 -->
- [x] Deploy specialized agents to `%USERPROFILE%\.claude\agents` <!-- id: 7 -->
- [x] Verify command registration in Claude Code (`/geo audit`) <!-- id: 8 -->

## Phase 3: Initial Audits & Baseline <!-- id: 9 -->
**Status**: ✅ Complete
- [x] Run benchmark audit on a test URL to verify scoring logic <!-- id: 10 -->
- [x] Test PDF report generation functionality <!-- id: 11 -->
- [x] Validate AI crawler analysis against standard `robots.txt` <!-- id: 12 -->

## Phase 4: Customization for Orbis <!-- id: 13 -->
**Status**: ✅ Complete
- [x] Customize `schema/` templates with Orbis-specific metadata <!-- id: 14 -->
- [x] Update `geo-report/` markdown templates with Orbis branding <!-- id: 15 -->
- [x] Modify `scripts/generate_pdf_report.py` for custom visual styling <!-- id: 16 -->

## Phase 5: Advanced Optimization & Scaling <!-- id: 17 -->
**Status**: ✅ Complete
- [x] Integrate TikTok, Threads, and BlueSky in `brand_scanner.py` <!-- id: 18 -->
- [x] Fine-tune `citability_scorer.py` for industry niches <!-- id: 19 -->
- [x] Implement batch auditing script for multiple URLs <!-- id: 20 -->

## Phase 6: Web Dashboard & Automation <!-- id: 21 -->
**Status**: ✅ Complete
- [x] Implement Node.js API server for audit control <!-- id: 22 -->
- [x] Build premium "glassmorphism" dashboard UI <!-- id: 23 -->
- [x] Integrate sequential script execution with real-time logs <!-- id: 24 -->
- [x] Add one-click PDF generation and viewing <!-- id: 25 -->

## Phase 7: AI Scoring & Scraper Enhancement <!-- id: 26 -->
**Status**: ✅ Complete
- [x] Refactor `brand_scanner.py` for real OpenAI analysis <!-- id: 27 -->
- [x] Implement automated `robots.txt` crawler auditing <!-- id: 28 -->
- [x] Enrich PDF reports with AI-generated fix examples and impact analysis <!-- id: 29 -->
- [x] Optimize PDF layout and spacing <!-- id: 30 -->

## Phase 8: Google Business Profile (GBP) Integration <!-- id: 31 -->
**Status**: ✅ Complete
- [x] Add GBP URL Input to Dashboard <!-- id: 32 -->
- [x] Create `gbp_analyzer.py` for AI Local Analysis <!-- id: 33 -->
- [x] Integrate GBP Data into PDF Report <!-- id: 34 -->
- [x] Verify End-to-End GBP Audit Flow <!-- id: 35 -->

## Phase 9: Post-Launch Polishing & Email Automation <!-- id: 36 -->
**Status**: ✅ Complete
- [x] Integrate Reoon Email Verification API for lead quality <!-- id: 37 -->
- [x] Implement dual-email automation (Notify Admin & Send Report to Subscriber) <!-- id: 38 -->
- [x] Add high-conversion Explainer Video placeholder with 16:9 thumbnail <!-- id: 39 -->
- [x] Fix PDF metadata (Proper Business Name in browser tab) <!-- id: 40 -->
- [x] Hide internal console controls for cleaner client experience <!-- id: 41 -->

## Phase 10: Site-Wide Dynamic Header <!-- id: 42 -->
**Status**: ✅ Complete
- [x] Implement site-wide Web Component header across all pages <!-- id: 43 -->
- [x] Add navigation routes: Home, Case Studio, More Orbis, Documentation <!-- id: 44 -->
- [x] Ensure single source of truth for global updates <!-- id: 45 -->

## Phase 11: Comprehensive Documentation <!-- id: 46 -->
**Status**: ✅ Complete
- [x] Implement sidebar layout with active tab highlighting <!-- id: 47 -->
- [x] Create 7 interactive documentation tabs <!-- id: 48 -->
- [x] Add rich content including listicles, charts, and graphs <!-- id: 49 -->

## Phase 12: Deployment Debugging <!-- id: 50 -->
**Status**: ✅ Complete
- [x] Investigate GitHub Actions logs <!-- id: 51 -->
- [x] Refactor `deploy.yml` for robustness <!-- id: 52 -->
- [x] Verify successful deployment via GitHub Actions <!-- id: 53 -->

## Phase 13: Case Studio Implementation <!-- id: 54 -->
**Status**: ✅ Complete
- [x] Implement side-by-side competitive comparison matrix <!-- id: 55 -->
- [x] Populate with BPS Zero Fees vs Orbis Local case study data <!-- id: 56 -->
- [x] Add visual score delta indicators and platform specific analysis <!-- id: 57 -->

## Phase 14: Potential Visibility & PDF Refinement <!-- id: 58 -->
**Status**: ✅ Complete
- [x] Add potential visibility score calculation to `gbp_grid.py` <!-- id: 59 -->
- [x] Update dashboard with current vs potential metrics <!-- id: 60 -->
- [x] Fix PDF layout overlaps and add decorative Spacers <!-- id: 61 -->
- [x] Integrate potential metrics into the final PDF report <!-- id: 62 -->

## Phase 15: Milestone 1 Finalization & AI Simulation Prep <!-- id: 63 -->
**Status**: ✅ Complete
- [x] Conduct final quality audit of Branding & Data Foundation <!-- id: 64 -->
- [x] Refactor common utility scripts for optimized AI model calls <!-- id: 65 -->
- [x] Prepare documentation for advanced GEO simulations <!-- id: 66 -->

# Milestone 2: Advanced AI Model Simulations <!-- id: 67 -->

## Phase 16: Simulation Engine & Logic Foundation <!-- id: 68 -->
**Status**: ✅ Complete
- [x] Create `scripts/sim_engine.py` for comparative GEO simulations <!-- id: 69 -->
- [x] Implement "Zero-Fee" baseline vs "Orbis" optimization logic <!-- id: 70 -->
- [x] Integrate OSM Nominatim API for GBP entity cross-validation (NAP+W check) <!-- id: 73 -->
- [x] Develop Confidence Scorer using OSM standard tags (`addr:street`, `website`, `brand:wikidata`) <!-- id: 74 -->
- [x] Update `gbp_analyzer.py` with OSM verification fallback mechanism <!-- id: 75 -->
- [x] Integrate simulation results into the Case Studio data flow <!-- id: 71 -->
- [x] Generate first automated simulation report (LightBox SEO) <!-- id: 72 -->

## Phase 17: Deep-Dive Data Strategy <!-- id: 76 -->
**Status**: 🗓️ Planned
- [ ] Implement a data schema to structure simulation results (`sim_schema.json`) <!-- id: 77 -->
- [ ] Connect simulation results to dashboard UI chart components <!-- id: 78 -->
- [ ] Update `generate_live_pdf.py` to include a full page "Simulation Comparison" block <!-- id: 79 -->
