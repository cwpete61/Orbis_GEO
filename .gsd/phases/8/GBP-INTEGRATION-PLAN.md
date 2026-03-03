---
phase: 8
plan: 1
wave: 1
---

# Plan: GBP Integration

## Objectives
- Add GBP URL input to the dashboard.
- Create `gbp_analyzer.py` for AI-powered local business analysis.
- Integrate GBP data into the PDF report.

## Tasks

### Wave 1: Frontend & API
#### Task 1: Update Dashboard UI
- **Action:** Add `gbpUrl` input to `index.html`.
- **Action:** Update `style.css` for new field alignment.
- **Verify:** Open dashboard and confirm field exists.

#### Task 2: Update Client Logic
- **Action:** Update `app.js` to send `gbpUrl` in audit requests.
- **Verify:** Inspect network request in browser when clicking "Run Full Audit".

#### Task 3: Update Server API
- **Action:** Update `server.js` to handle `gbpUrl` and pass to scripts.
- **Verify:** Check if `server.js` correctly maps `gbpUrl` from req body.

### Wave 2: Analysis Engine
#### Task 4: Create GBP Analyzer
- **Action:** Implement `scripts/gbp_analyzer.py` using OpenAI and DDGS.
- **Verify:** Run `python scripts/gbp_analyzer.py "https://maps.app.goo.gl/..."` and check `test_gbp.json`.

### Wave 3: Reporting & Integration
#### Task 5: PDF Data Aggregation
- **Action:** Update `generate_live_pdf.py` to read `test_gbp.json`.
- **Verify:** Run script and check if `data['gbp']` is populated.

#### Task 6: PDF Template Update
- **Action:** Update `generate_pdf_report.py` to add a GBP Analysis page.
- **Verify:** Generate PDF and confirm new page exists with real data.
