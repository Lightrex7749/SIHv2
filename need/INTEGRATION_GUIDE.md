# Integration Guide (v2)

## Development Strategy

DrishtiSetu uses a mock-first integration strategy. The frontend must initially communicate with mock backend responses. Individual modules can then replace mock implementations one by one.

---

## Integration Order (now with dated checkpoints — see CONTRIBUTING.md §7 for the full table)

### Stage 1 — Frontend + Backend skeleton
### Stage 2 — Mock habitation data
### Stage 3 — Mock risk engine (+ `/risk/explain` mock, NEW)
### Stage 4 — Mock relocation recommendation (+ `status`/`estimated_cost` fields, NEW)
### Stage 5 — GIS map layers (+ `land_use_zones` layer, NEW)
### Stage 6 — Real ML risk engine (documented formula, NEW requirement)
### Stage 7 — Real CV module (with `model_disclosure` field, NEW)
### Stage 8 — RAG retrieval (with `evidence_sufficient` path, NEW requirement)
### Stage 9 — Agentic decision layer (with deterministic capacity-safety enforcement, NEW requirement)
### Stage 10 — End-to-end testing + `decision_log` Accept/Reject flow (NEW) + demo rehearsal (NEW)

---

## Golden Rule

Never wait until every module is finished before integration. Integrate continuously, against dated checkpoints (CONTRIBUTING.md §7), not open-ended timelines.

---

## End-to-End Flow (v2)

```text
User selects habitation
        ↓
Frontend
        ↓
GET habitation
        ↓
Decision API
        ↓
Risk analysis (+ explainability breakdown)
        ↓
Vulnerability analysis
        ↓
GIS candidate sites (+ land-use conflict check)
        ↓
Relocation analysis
        ↓
Capacity analysis (deterministic, LLM cannot override)
        ↓
RAG evidence (or explicit "insufficient evidence")
        ↓
Decision Agent
        ↓
Final recommendation (+ estimated cost)
        ↓
Frontend dashboard
        ↓
Authority Accept / Reject / Defer → decision_log (NEW, terminal step)
```

---

## Mock-First Requirement

Every major module must initially support deterministic mock output. The API contract must remain unchanged when the mock implementation is replaced by the real implementation.

**New requirement:** every mock and every real implementation must pass the shared contract test suite (`/tests/contract/`) before merge — this is what actually enforces "the contract must remain unchanged," rather than relying on manual discipline alone.

---

## Demo-Readiness Checklist (NEW)

Before final rehearsal, confirm the following are live and demoable end-to-end:

- [ ] `/risk/explain` renders a visible factor breakdown in the UI
- [ ] At least one seeded habitation uses real pilot-district data (not synthetic)
- [ ] Capacity-safety test passes live (demo an attempted LLM override and show it's rejected)
- [ ] At least one RAG query intentionally triggers the "insufficient evidence" response
- [ ] Land-use conflict flag displays on at least one candidate site
- [ ] Accept/Reject/Defer panel writes to `decision_log` and the entry is visible on reload
- [ ] Language toggle switches at least the dashboard's primary labels
