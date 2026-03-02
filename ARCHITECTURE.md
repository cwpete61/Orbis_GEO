# ARCHITECTURE

## Overview
The GEO-SEO Claude Code Skill is a modular tool designed to perform comprehensive audits for AI search engine optimization (GEO). It utilizes a multi-agent architecture where a central orchestrator delegates specialized tasks to parallel subagents and sub-skills.

## Components

### 1. Skill Orchestrator (`geo/`)
- **SKILL.md**: The primary entry point. It handles user commands (e.g., `/geo audit`) and routes them to the appropriate sub-skills and agents.

### 2. Specialized Sub-skills (`skills/`)
- 11 modular skills that handle specific aspects of the audit:
  - `geo-audit`: Orchestrates the full audit flow.
  - `geo-citability`: Logic for AI citation scoring.
  - `geo-brand-mentions`: Cross-platform brand scanning.
  - `geo-schema`: Validation and generation of JSON-LD schemas.
  - ...and others for crawlers, technical SEO, content, and reporting.

### 3. Parallel Subagents (`agents/`)
- Claude-specific agent definitions that provide expert guidance for different domains:
  - `geo-ai-visibility.md`
  - `geo-platform-analysis.md`
  - `geo-technical.md`
  - `geo-content.md`
  - `geo-schema.md`

### 4. Utility Scripts (`scripts/`)
- Python-based backend logic for data-intensive tasks:
  - `fetch_page.py`: Robust HTML fetching and parsing.
  - `citability_scorer.py`: Algorithmic scoring of content passages.
  - `brand_scanner.py`: Platform-specific API/scraping logic.
  - `generate_pdf_report.py`: PDF generation using ReportLab.

### 5. Schema Templates (`schema/`)
- Pre-defined JSON-LD templates for various business types (Organization, LocalBusiness, Article, etc.) to ensure AI discoverability.

## Data Flow
1. User invokes `/geo audit <url>`.
2. Orchestrator fetches the target page.
3. Orchestrator launches 5 subagents in parallel.
4. Each subagent utilizes relevant sub-skills and Python scripts.
5. Results are aggregated into a composite GEO Score.
6. A final report is generated in Markdown or PDF format.
