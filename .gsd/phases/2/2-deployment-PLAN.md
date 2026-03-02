---
phase: 2
plan: 1
wave: 1
---

# Phase 2: Tool Deployment Plan

## Goal
Deploy the `geo-seo-claude` skills and agents to the Claude Code environment to enable `/geo` commands.

## Tasks

### 1. Initialize Claude Code Directory <!-- id: 2.1 -->
Ensure the `.claude` configuration directory structure exists in the user's home directory.
- [ ] Create `C:\Users\crawf\.claude\skills` and `C:\Users\crawf\.claude\agents`.

### 2. Deploy Main GEO Skill <!-- id: 2.2 -->
Copy the core orchestrator files.
- [ ] Copy contents of `geo/` to `C:\Users\crawf\.claude\skills\geo\`.

### 3. Deploy Sub-skills <!-- id: 2.3 -->
Iterate through the `skills/` directory and copy each sub-skill.
- [ ] Copy `skills/geo-*` to `C:\Users\crawf\.claude\skills\`.

### 4. Deploy Subagents <!-- id: 2.4 -->
Copy the specialized markdown agents.
- [ ] Copy `agents/*.md` to `C:\Users\crawf\.claude\agents\`.

### 5. Transfer Supporting Assets <!-- id: 2.5 -->
Ensure Python scripts and schema templates are in place within the skill directory.
- [ ] Copy `scripts/` and `schema/` to `C:\Users\crawf\.claude\skills\geo\`.

## Verification
- [ ] List contents of `C:\Users\crawf\.claude\skills\geo` to verify files.
- [ ] Check if `geo-audit` skill exists in `.claude\skills`.
- [ ] Check if `geo-ai-visibility.md` exists in `.claude\agents`.
