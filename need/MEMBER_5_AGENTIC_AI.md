You are Member 5 of the DrishtiSetu SIH 2026 development team. (v2 brief)

ROLE:
Agentic AI + Relocation Decision Engineer

==================================================
WHAT'S NEW IN v2 (read this first)
==================================================

Your original brief already contained the right instinct ("do not let the
LLM override numerical constraints"). The audit upgraded this from a
principle into a **structural requirement with a required test**:

1. `capacity_sufficient` must be computed as a **pure deterministic boolean
   in code** — `population_to_relocate <= site_capacity * safety_margin` —
   BEFORE any LLM call. Pass it into the LLM prompt as a fixed, stated fact
   ("The following is true and must not be contradicted: capacity_sufficient
   = false"). The LLM may explain or summarize but must never recompute or
   contradict it.
2. You must write a unit test that deliberately tries to trick the LLM
   (e.g., a prompt injection or misleading instruction) into contradicting
   this value, and asserts the API output is unaffected. This test should be
   part of your demo script (see DEMO_FLOW.md v2, Step 7).
3. Add a new deterministic **land-use conflict check** into your candidate
   site ranking (consume the `land_use_conflict` field GIS/Member 3 now
   produces) — down-rank or flag conflicting sites, and say why in the
   reasoning output.
4. Add a new, optional **`estimated_cost`** calculation to your relocation
   recommendation (population_to_relocate × a documented per-capita
   resettlement benchmark — see DATA_SOURCES.md v2). If no reliable
   benchmark exists, return `null` and say so — never invent a number.
5. Your `/relocation/recommend` output now includes a `status` field
   (PROPOSED by default) that Member 6's decision-log flow will update.

==================================================
MANDATORY DOCUMENTS
==================================================

Read before coding (v2 versions):
/docs/ARCHITECTURE.md
/docs/API_CONTRACT.md
/docs/DATABASE_SCHEMA.md
/docs/DATA_SOURCES.md
/docs/CONTRIBUTING.md
/docs/INTEGRATION_GUIDE.md
/docs/DEMO_FLOW.md

==================================================
OWNERSHIP
==================================================

Primary ownership: /agents/ and /relocation/
Agents: /agents/risk_agent, /agents/vulnerability_agent, /agents/relocation_agent,
/agents/capacity_agent, /agents/decision_agent
Relocation: /relocation/site_selection, /relocation/capacity

Do not independently rewrite ML, CV, GIS, or RAG implementations.

==================================================
OBJECTIVE
==================================================

Build the agentic decision-support layer that coordinates structured
outputs from the ML risk engine, vulnerability engine, computer vision, GIS
(including the new land-use conflict layer), disaster history, population
information, relocation-site analysis, carrying-capacity analysis, and RAG
evidence — producing an explainable relocation recommendation.

==================================================
AGENT DESIGN (unchanged roles)
==================================================

* Risk Agent — consumes hazard/risk information
* Vulnerability Agent — consumes population/vulnerability indicators
* Relocation Agent — identifies and ranks candidate sites (NEW: now factors
  in `land_use_conflict`)
* Capacity Agent — checks whether candidate sites can accommodate the
  affected population (NEW: this must be the deterministic source of truth
  for `capacity_sufficient`, computed before any LLM call)
* Decision Agent — combines all outputs into the final recommendation
  (NEW: includes estimated cost where available)

==================================================
IMPORTANT (unchanged, now with a required test)
==================================================

Agents must NOT simply generate arbitrary text. Use structured
tools/functions/API calls. The decision should be based primarily on
structured evidence. LLM reasoning may be used for explanation,
summarization, evidence synthesis, and prioritization reasoning.
Deterministic calculations must be used for anything numeric and safety-
critical — see the capacity-safety requirement above, which is now a
required unit test, not just an instruction to the LLM.

==================================================
RELOCATION FACTORS (unchanged list + land-use conflict)
==================================================

1. Residual hazard
2. Site suitability
3. Available area
4. Estimated carrying capacity
5. Population to relocate
6. Road accessibility
7. Healthcare accessibility
8. Water availability
9. School accessibility
10. Shelter availability
11. Distance
12. Historical hazard exposure
13. (NEW) Land-use conflict status

Do not invent unavailable measurements.

==================================================
API — /api/v1/relocation/recommend (v2 fields)
==================================================

Input: `{"habitation_id": "H001"}`

Output (NEW fields: land_use_conflict, estimated_cost, cost_basis, status):
```json
{
  "habitation_id": "H001",
  "recommended_site": {"site_id": "S001", "name": "Candidate Site A", "land_use_conflict": false},
  "suitability_score": 84.5,
  "site_capacity": 1800,
  "population_to_relocate": 1250,
  "capacity_sufficient": true,
  "estimated_cost": 62500000,
  "cost_basis": "population_to_relocate x per_capita_resettlement_benchmark",
  "recommendation": "SUITABLE",
  "status": "PROPOSED"
}
```

==================================================
MAIN DECISION API — /api/v1/decision/analyze
==================================================

Unchanged coordination role: habitation retrieval, risk analysis,
vulnerability analysis, relocation-site analysis (now with land-use check),
capacity analysis (deterministic), RAG evidence retrieval (now with
`evidence_sufficient` handling), final decision synthesis. Output must
follow `/docs/API_CONTRACT.md` v2.

==================================================
MOCK MODE
==================================================

Implement mock versions of unavailable dependencies (risk service, RAG, GIS)
with the same final API structure, including all new v2 fields.

==================================================
EXPLAINABILITY
==================================================

Return reasoning such as: high hazard exposure, high vulnerability, repeated
historical events, candidate site has sufficient estimated capacity,
candidate site has lower residual hazard, better access to essential
services, and (NEW) "no land-use conflict detected on candidate site" or
"candidate site excluded due to eco-sensitive zone overlap" where relevant.
Do not invent reasons that are not supported by the data.

==================================================
TESTING (v2 — new required tests)
==================================================

Test: high-risk habitation, low-risk habitation, insufficient capacity,
suitable site, unsuitable sites, no candidate site, missing RAG, missing CV,
missing GIS, complete mock end-to-end workflow, AND:

* (NEW, required) capacity-safety adversarial test: feed the LLM a prompt
  designed to make it claim sufficiency when `population_to_relocate >
  site_capacity`, and assert the API response still correctly returns
  `capacity_sufficient: false`.
* (NEW) land-use conflict correctly excludes/flags a conflicting site.
* (NEW) estimated_cost returns null (not a fabricated number) when no
  benchmark is configured.

==================================================
CRITICAL RULE (now backed by the test above)
==================================================

Do not allow the LLM to override numerical constraints. If
`population_to_relocate > site_capacity`, the system must not state that
capacity is sufficient merely because an LLM generated such a statement.
Structured calculations take precedence, and this must be provably true via
the adversarial test above — not just asserted in this document.

==================================================
AI CODING RULES
==================================================

Do not: build a separate chatbot, create another backend, modify API
contracts, modify database schema independently, fabricate site capacity,
fabricate hazard data, fabricate sources, make autonomous real-world
relocation decisions.

Before completion: run tests (including the new adversarial capacity test),
test mock end-to-end flow, verify API output, verify capacity logic, verify
reasoning is evidence-based, list dependencies, list limitations.

FINAL PRINCIPLE:

Build an agentic decision-support orchestrator, not an autonomous authority.
The system recommends and explains; authorized disaster-management
authorities make the final decision — and now that decision is provably
protected from being overridden by generative text, which is exactly the
kind of guardrail a technical judging panel will want to see proven, not
just claimed.
