# ROADMAP

## Phase 1: Environment Readiness <!-- id: 0 -->
- [ ] Verify Python 3.8+ installation <!-- id: 1 -->
- [ ] Install Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) <!-- id: 2 -->
- [ ] Install Python dependencies from `requirements.txt` <!-- id: 3 -->
- [ ] Install Playwright for screenshot capabilities <!-- id: 4 -->

## Phase 2: Tool Deployment <!-- id: 5 -->
- [ ] Manually map and copy `geo-seo-claude` skills to the Claude Code configuration directory (`%USERPROFILE%\.claude\skills`) <!-- id: 6 -->
- [ ] Deploy specialized agents to `%USERPROFILE%\.claude\agents` <!-- id: 7 -->
- [ ] Verify command registration in Claude Code (`/geo audit`) <!-- id: 8 -->

## Phase 3: Initial Audits & Baseline <!-- id: 9 -->
- [ ] Run benchmark audit on a test URL to verify scoring logic <!-- id: 10 -->
- [ ] Test PDF report generation functionality <!-- id: 11 -->
- [ ] Validate AI crawler analysis against standard `robots.txt` <!-- id: 12 -->

## Phase 4: Customization for Orbis <!-- id: 13 -->
- [ ] Customize `schema/` templates with Orbis-specific metadata <!-- id: 14 -->
- [ ] Update `geo-report/` markdown templates with Orbis branding <!-- id: 15 -->
- [ ] Modify `scripts/generate_pdf_report.py` for custom visual styling <!-- id: 16 -->

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

---

# Project Complete
The **GEO-SEO Claude Code Tool** is fully deployed, branded for Orbis, and optimized for advanced AI search visibility auditing.
