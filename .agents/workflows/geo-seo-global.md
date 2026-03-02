---
description: Perform a full Orbis GEO-SEO Global Audit for a target URL.
---

1. Ensure the environment is ready.
   - [ ] Run `python --version` (Requires 3.8+)
   - [ ] Run `claude --version` (Requires Claude Code CLI)

2. Perform Multi-Platform Brand Analysis
   - [ ] Run `python scripts/brand_scanner.py "[BRAND_NAME]"`
   - Note: This checks YouTube, TikTok, Reddit, Wikipedia, LinkedIn, and more.

3. Execute Technical & Citability Audit
   - [ ] Run `python scripts/fetch_page.py [URL] > audit_fetch.json`
   - [ ] Run `python scripts/citability_scorer.py [URL] --niche [NICHE] > audit_score.json`
   - [ ] Run `python scripts/llmstxt_generator.py [URL] > audit_crawlers.json`

4. Generate Branded Client Deliverable
   - [ ] Run `python scripts/generate_pdf_report.py`
   - [ ] Rename the output: `copy GEO-REPORT-sample.pdf [BRAND]-GEO-AUDIT.pdf`

5. Verify & Deliver
   - [ ] Inspect `[BRAND]-GEO-AUDIT.pdf` for Orbis branding and accuracy.
   - [ ] Deliver the PDF and JSON audit files to the client.
