---
phase: 5
plan: 1
wave: 1
---

# Phase 5: Advanced Optimization & Scaling Plan

## Goal
Enhance the tool's competitive capabilities through social signal expansion, niche-specific scoring, and batch processing.

## Tasks

### 1. Extend Brand Scanner <!-- id: 5.1 -->
Add support for emerging social signals that influence AI citation graphs.
- [ ] Add TikTok and Instagram Reels check logic (video content is high-signal).
- [ ] Add Threads and BlueSky to "Other Platforms" for modern entity validation.

### 2. Niche-Specific Citability <!-- id: 5.2 -->
Refine the scoring algorithm for different industries.
- [ ] Implement "Niche Modes" in `citability_scorer.py`:
  - **YMYL (Legal/Medical)**: Heavier weighting on credentials and verified sources.
  - **Technical/SaaS**: Weighting for code blocks and implementation examples.
  - **E-commerce**: Weighting for product specs and comparison data.

### 3. Implement Batch Auditing <!-- id: 5.3 -->
Create a utility to audit entire site sections or domain lists.
- [ ] [NEW] `scripts/batch_audit.py`:
  - Read URLs from a CSV or text file.
  - Run the full suite of GEO scripts for each.
  - Generate a combined summary JSON for all results.

## Verification
- [ ] Run `brand_scanner.py` for "Orbis" and verify new platform URLs.
- [ ] Test `citability_scorer.py` in `--niche technical` mode on a technical page.
- [ ] Run `batch_audit.py` on a list of 3 URLs and verify output.
