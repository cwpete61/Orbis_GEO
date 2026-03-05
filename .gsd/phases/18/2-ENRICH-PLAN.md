---
phase: 18
plan: 2
wave: 2
---

# Wave 2: Intelligent Enrichment

Modify Python analysis scripts to utilize the verified data from Outscraper.

## Context
- `scripts/brand_scanner.py`: Platform analysis.
- `scripts/gbp_analyzer.py`: GBP insights.

## Tasks

### 1. Brand Scanner Update
- [ ] Modify `brand_scanner.py` to read `test_outscraper_contacts.json`.
- [ ] Priority-merge verified social links into the `platforms` results.

### 2. GBP Analyzer Update
- [ ] Modify `gbp_analyzer.py` to ingest `test_outscraper_maps.json`.
- [ ] Update the AI prompt to include rating, review count, and attributes for factual grounding.

## Verification
- [ ] Run `python scripts/brand_scanner.py` with mock Outscraper data.
- [ ] Run `python scripts/gbp_analyzer.py` and check if AI insights reflect the hard data.
