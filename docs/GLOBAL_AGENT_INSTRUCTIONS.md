========================================================
DRISHTISETU — GLOBAL AI AGENT INSTRUCTIONS (v2)
========================================================

You are working as ONE of six AI-assisted development agents
on the same DrishtiSetu SIH 2026 repository.

This is NOT six independent projects. The repository is a shared
integrated system, now hardened with hackathon-credibility fixes
based on a pre-submission audit. Read the v2 note in each doc below.

MANDATORY SOURCE OF TRUTH:

/docs/ARCHITECTURE.md          (v2 — explainability, decision log, land-use check, security note)
/docs/API_CONTRACT.md          (v2 — new endpoints: /risk/explain, /decision/log)
/docs/DATABASE_SCHEMA.md       (v2 — new tables: decision_log, land_use_zones)
/docs/DATA_SOURCES.md          (v2 — real named datasets, scoring methodology section)
/docs/CONTRIBUTING.md          (v2 — contract testing requirement, dated checkpoints)
/docs/INTEGRATION_GUIDE.md     (v2 — demo-readiness checklist)
/docs/DEMO_FLOW.md             (v2 — explainability + guardrail demo moments)

READ THESE BEFORE CODING. All v2 changes are additive — no v1 field
was renamed or removed. If your existing code already matches v1,
you are only ADDING to it, not rewriting it.

========================================================
NON-NEGOTIABLE RULES (unchanged + 3 new)
========================================================

1. Do not redesign the architecture.
2. Do not independently change API contracts.
3. Do not independently change database schemas.
4. Do not create a separate application.
5. Do not create a second backend.
6. Do not create a second database.
7. Do not duplicate another member's functionality.
8. Stay primarily inside your assigned module.
9. Use mock implementations whenever dependencies are incomplete, clearly labeled as mock.
10. Preserve the same input/output structure between mock and production implementations.
11. Write tests for your module.
12. Never fabricate real-world data.
13. Never fabricate citations or sources.
14. Never claim model accuracy without evaluation.
15. Never commit API keys, passwords, tokens, or .env files.
16. Do not silently modify shared documentation.
17. Do not silently modify another member's code.
18. Inspect existing code before creating new code.
19. Prefer simple, modular, replaceable implementations.
20. Every change must keep the main integration path functional.

21. (NEW) Never let LLM-generated text override a deterministic numeric
    calculation — especially `capacity_sufficient`. Compute it in code
    first, pass it to any LLM call as a fixed fact, and test that the
    LLM cannot contradict it.

22. (NEW) Any score, confidence value, or classification your module
    returns must be traceable to a documented formula or model —
    never an unexplained number. If asked "why this value?", there
    must be a real answer, ideally via an API endpoint.

23. (NEW) Every PR must pass the shared contract test suite
    (`/tests/contract/`) against `API_CONTRACT.md` before merge.

========================================================
WHEN YOU NEED SOMETHING FROM ANOTHER MODULE
========================================================

Use the API/interface defined in /docs/API_CONTRACT.md.
If that module is not ready, USE A MOCK. Do NOT recreate that module yourself.

========================================================
BEFORE CODING
========================================================

1. Inspect repository structure.
2. Read all mandatory documentation (v2 versions).
3. Inspect existing code in your module.
4. Identify existing interfaces.
5. Confirm your ownership boundaries.
6. Create a short implementation plan, explicitly noting which
   v2 additions (explainability, decision log, land-use check,
   capacity safety, real data sourcing) apply to your module.
7. Then code.

========================================================
AFTER CODING
========================================================

1. Run tests.
2. Check lint/type errors where applicable.
3. Verify API compatibility via the contract test suite.
4. Verify no unrelated files were changed.
5. Verify mock compatibility.
6. Report files changed.
7. Report dependencies added.
8. Report tests performed.
9. Report limitations.
10. Report anything requiring integration attention.
11. (NEW) Confirm whether your module's v2 requirement (see your
    individual brief) is implemented and demoable, and report its
    status explicitly.

========================================================
GOLDEN RULE
========================================================

ARCHITECTURE > INDIVIDUAL AGENT PREFERENCE
API CONTRACT > INDIVIDUAL IMPLEMENTATION PREFERENCE
DATABASE SCHEMA > INDIVIDUAL IMPLEMENTATION PREFERENCE
INTEGRATION > LOCAL OPTIMIZATION
EXPLAINABILITY AND ACCOUNTABILITY > RAW MODEL SOPHISTICATION

A working, explainable, accountable integrated prototype is the priority.
========================================================
