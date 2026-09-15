# DrishtiSetu v2 — Start Here

This folder replaces your original 14 files with a v2 set that has the
audit fixes baked directly into the instructions, so any AI coding agent
(Claude Code, Cursor, etc.) you point at a file will build the fixed
version automatically — you don't need to separately explain the fixes.

## What changed and why

Read `DRISHTISETU_AUDIT_AND_UPGRADE.md` (in the parent folder) first if you
haven't already — it explains the reasoning behind every change below.
Short version: your architecture was already strong; the gaps were
**credibility gaps** (unexplained scores, no real data, no accountability
trail), not engineering gaps. Every v2 addition targets exactly one of
those three gaps.

## File map (old name → new name)

| Old file | New file | What's new in it |
|---|---|---|
| architecture doc | `ARCHITECTURE.md` | explainability endpoint, decision log, land-use check, security note, published scoring formula |
| API contract | `API_CONTRACT.md` | `/risk/explain`, `/decision/log` (POST+GET), new fields on relocation/vision/RAG responses |
| database schema | `DATABASE_SCHEMA.md` | `decision_log` table, `land_use_zones` table, new fields |
| contribution rules | `CONTRIBUTING.md` | contract-testing requirement, dated integration checkpoints |
| data sources | `DATA_SOURCES.md` | real named Indian datasets, scoring-methodology section, cost-benchmark section |
| integration guide | `INTEGRATION_GUIDE.md` | demo-readiness checklist |
| demo flow | `DEMO_FLOW.md` | explainability + guardrail demo moments, Authority Action step |
| global agent instructions | `GLOBAL_AGENT_INSTRUCTIONS.md` | 3 new non-negotiable rules |
| Member 1 (ML) prompt | `MEMBER_1_ML_RISK.md` | scoring formula + explainability endpoint requirements |
| Member 2 (CV) prompt | `MEMBER_2_COMPUTER_VISION.md` | model_disclosure field, change-detection framing |
| Member 3 (GIS) prompt | `MEMBER_3_GIS_DATA.md` | real pilot-district data, land-use conflict layer |
| Member 4 (RAG) prompt | `MEMBER_4_RAG_NLP.md` | evidence_sufficient field/path |
| Member 5 (Agentic AI) prompt | `MEMBER_5_AGENTIC_AI.md` | deterministic capacity-safety test, cost estimation |
| Member 6 (Full-stack) prompt | `MEMBER_6_FULLSTACK_INTEGRATION.md` | decision log UI, explainability drawer, contract test suite ownership |

## How to use this with your AI coding agents

1. Replace your existing `/docs/*.md` files in the repo with this set
   (same folder structure — put these in `/docs/`).
2. Give each team member's AI agent (Claude Code, etc.) their matching
   `MEMBER_X_*.md` file as the system/task prompt, exactly as you were
   already doing — the v2 files are drop-in replacements, same role,
   same ownership boundaries, just with the new requirements folded in.
3. Point every agent at `GLOBAL_AGENT_INSTRUCTIONS.md` as the shared
   baseline, same as before.
4. Everything is additive — no v1 field, table, or endpoint was renamed
   or removed, so if any module is already partially built against the
   old contract, it will not break; the agent just needs to add the new
   pieces on top.

## Minimum bar to actually be demo-ready (not just "coded")

Before you call this done, walk through the checklist in
`INTEGRATION_GUIDE.md` → "Demo-Readiness Checklist" and the 9-step script
in `DEMO_FLOW.md`. A feature that exists in code but was never rehearsed
live is the most common way teams lose points they'd otherwise have earned.
