# ROADMAP

## Phase 1: Environment Readiness <!-- id: 0 -->
- [x] Verify Python 3.8+ installation <!-- id: 1 -->
- [x] Install Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) <!-- id: 2 -->
- [x] Install Python dependencies from `requirements.txt` <!-- id: 3 -->
- [x] Install Playwright for screenshot capabilities <!-- id: 4 -->

## Phase 2: Tool Deployment <!-- id: 5 -->
- [x] Manually map and copy `geo-seo-claude` skills to the Claude Code configuration directory (`%USERPROFILE%\.claude\skills`) <!-- id: 6 -->
- [x] Deploy specialized agents to `%USERPROFILE%\.claude\agents` <!-- id: 7 -->
- [x] Verify command registration in Claude Code (`/geo audit`) <!-- id: 8 -->

## Phase 3: Initial Audits & Baseline <!-- id: 9 -->
- [x] Run benchmark audit on a test URL to verify scoring logic <!-- id: 10 -->
- [x] Test PDF report generation functionality <!-- id: 11 -->
- [x] Validate AI crawler analysis against standard `robots.txt` <!-- id: 12 -->

## Phase 4: Customization for Orbis <!-- id: 13 -->
- [x] Customize `schema/` templates with Orbis-specific metadata <!-- id: 14 -->
- [x] Update `geo-report/` markdown templates with Orbis branding <!-- id: 15 -->
- [x] Modify `scripts/generate_pdf_report.py` for custom visual styling <!-- id: 16 -->

## Phase 5: Advanced Optimization & Scaling <!-- id: 17 -->
**Status**: ✅ Complete
- [x] Integrate additional brand mention platforms in `brand_scanner.py` <!-- id: 18 -->
- [x] Fine-tune `citability_scorer.py` for industry niches <!-- id: 19 -->
- [x] Implement batch auditing script for multiple URLs <!-- id: 20 -->

## Phase 6: Local Business (GBP) Integration <!-- id: 18 -->
**Status**: ✅ Complete
- [x] Add Google Maps presence check to `brand_scanner.py` <!-- id: 19 -->
- [x] Implement Local Citation check (Yelp, BBB, Local Directories) <!-- id: 20 -->
- [x] Update `local-business.json` documentation for GBP linking <!-- id: 21 -->
- [x] Add "Local Visibility" section to the PDF report generator <!-- id: 22 -->

## Phase 7: Orbis Local Dashboard <!-- id: 23 -->
**Status**: ✅ Complete
- [x] Implement Node.js backend to bridge audits to a web UI <!-- id: 24 -->
- [x] Build premium dark-mode interface for report management <!-- id: 25 -->
- [x] Enable real-time script logging and PDF download via UI <!-- id: 26 -->

## Phase 16: Automated Simulation Pipeline <!-- id: 27 -->
**Status**: ✅ Complete
- [x] Implement Simulation Engine base logic. <!-- id: 28 -->
- [x] Allow running Baseline vs Optimized comparisons. <!-- id: 29 -->
- [x] Store data locally for pipeline ingestion. <!-- id: 30 -->

## Phase 17: Deep-Dive Data Strategy <!-- id: 31 -->
**Status**: ✅ Complete
### Wave 1: Data Architecture
- [x] Create `schema/sim_schema.json` to define `sim_engine.py` output.
- [x] Create baseline, optimized, and delta objects in the schema.
- [x] Ensure `sim_engine.py` adheres to the schema format.
- [x] Update `scripts/generate_live_pdf.py` to aggregate the simulated data payload.

### Wave 2: Dashboard UI Connection
- [x] Review `dashboard/index.html` structure.
- [x] Update `dashboard/server.js` with a new endpoint to fetch `/api/simulation-data`.
- [x] Update `dashboard/app.js` to render the simulation data into the visual map UI tiles (Pot. Reach, Pot. Fallout).

### Wave 3: PDF Generation Upgrades
- [x] Review `scripts/generate_pdf_report.py`.
- [x] Replace static dummy potential scores with dynamic simulated data.
- [x] Add a distinct 'Simulation Comparison Insights' block to the 'GEO Visibility & Search Fallout' section of the PDF, explicitly showing growth deltas.

## Phase 18: Outscraper & Social Media Verified Integration <!-- id: 32 -->
**Status**: 🏗 In Progress
### Wave 1: Verification Infrastructure
- [ ] Implement Outscraper Webhook listener in `server.js`.
- [ ] Connect Google Maps Data & Review APIs.
- [ ] Connect Emails & Contacts Scraper for legal social link verification.

### Wave 2: Intelligent Enrichment
- [ ] Update `gbp_analyzer.py` to ingest and analyze hard Maps data.
- [ ] Update `brand_scanner.py` to prioritize verified social links.
- [ ] Refactor `generate_live_pdf.py` to aggregate hybrid data (Verified + Community).

### Wave 3: UI & Reporting
- [ ] Update PDF templates to display "Verified" badges for Outscraper data.
- [ ] Add Keyword Gap analysis block (based on real reviews) to the PDF.
- [ ] Verify full end-to-end integration.

---

# Project Roadmap Continued...
The **GEO-SEO Claude Code Tool** is being enhanced with enterprise-grade data providers.
