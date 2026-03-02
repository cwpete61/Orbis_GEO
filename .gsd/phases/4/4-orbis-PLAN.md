---
phase: 4
plan: 1
wave: 1
---

# Phase 4: Orbis Customization Plan

## Goal
Tailor the GEO-SEO tool's outputs (Schema, Reports, PDF) to the Orbis brand identity.

## Tasks

### 1. Customize Schema Templates <!-- id: 4.1 -->
Update the JSON-LD templates with Orbis-specific metadata markers.
- [ ] Update `schema/organization.json` with Orbis info (or generic Orbis placeholders).
- [ ] Update `schema/local-business.json` for Orbis GEO services.

### 2. Update Report Branding <!-- id: 4.2 -->
Modify the markdown report generation instructions.
- [ ] Update `skills/geo-report/SKILL.md` to use "Orbis GEO-SEO" as the primary branding.
- [ ] Update header/footer text in reports to reference Orbis.

### 3. Customize PDF Styling <!-- id: 4.3 -->
Inject Orbis brand colors and logo placeholders into the PDF generator.
- [ ] Modify `scripts/generate_pdf_report.py`:
  - Update `PRIMARY`, `ACCENT`, and `HIGHLIGHT` colors.
  - Add "Orbis GEO-SEO" to the header/footer drawing logic.
  - (Optional) Add a placeholder for an Orbis logo if applicable.

## Verification
- [ ] Verify `schema/organization.json` contains "Orbis".
- [ ] Generate a sample PDF and verify the new color palette.
- [ ] Check `GEO-CLIENT-REPORT.md` template for Orbis references.
