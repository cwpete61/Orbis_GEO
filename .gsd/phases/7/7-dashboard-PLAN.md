---
phase: 7
plan: 1
wave: 1
---

# Phase 7: Orbis Local Dashboard

## Goal
Implement a functional web-based control panel to run Orbis Local audits.

## Tasks

### 1. Initialize Dashboard Backend <!-- id: 7.1 -->
- [ ] Create `dashboard/server.js` with Express.
- [ ] Implement `POST /api/audit` to execute the full audit sequence.
- [ ] Implement `POST /api/step` to execute individual Python scripts.

### 2. Implement Dashboard Frontend <!-- id: 7.2 -->
- [ ] Create `dashboard/index.html` with Brand/URL inputs and control buttons.
- [ ] Create `dashboard/style.css` with Orbis Local branding (premium dark mode).
- [ ] Create `dashboard/app.js` to handle UI interactions and script logging.

### 3. Verification <!-- id: 7.3 -->
- [ ] Start server and verify UI renders.
- [ ] Trigger a manual "Fetch" step and verify JSON output.
- [ ] Trigger a "Full Audit" and verify PDF generation.

## Verification
- Dashboard accessible at `http://localhost:3000`.
- PDF generated successfully via UI button.
