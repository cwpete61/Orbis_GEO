---
phase: 3
plan: 1
wave: 1
---

# Phase 3: Initial Audits & Baseline Plan

## Goal
Verify the end-to-end functionality of the deployed GEO-SEO tool using benchmark targets.

## Tasks

### 1. Benchmark Audit <!-- id: 3.1 -->
Run a full audit on a known URL to verify scoring and orchestration logic.
- [ ] Run `claude` and execute `/geo audit https://example.com` (Note: I will simulate this by running the scripts directly since I can't interact with the Claude CLI).
- [ ] Run `python scripts/fetch_page.py --url https://example.com` and verify output.
- [ ] Run `python scripts/citability_scorer.py --url https://example.com` and verify scoring.

### 2. Test PDF Report Generation <!-- id: 3.2 -->
Validate the PDF engine and visualization logic.
- [ ] Run `python scripts/generate_pdf_report.py` with sample audit data.
- [ ] Verify the creation of `report.pdf`.

### 3. AI Crawler Analysis Validation <!-- id: 3.3 -->
Check if the crawler analysis correctly identifies AI bots.
- [ ] Run `python scripts/llmstxt_generator.py` for a test domain.
- [ ] Verify `llms.txt` output format.

## Verification
- [ ] Successful data extraction from `fetch_page.py`.
- [ ] Validated numeric score from `citability_scorer.py`.
- [ ] Viewable `report.pdf` (I will check file existence and size).
- [ ] Correct formatting in `llms.txt`.
