# Contribution Rules (v2)

## 1. Repository Rule

DrishtiSetu is ONE integrated project. Do not create separate repositories for individual modules.

---

## 2. Branches

```text
main

feature/risk-engine
feature/computer-vision
feature/gis-data
feature/rag-nlp
feature/agentic-ai
feature/platform-integration
```

`main` must remain runnable at all times.

---

## 3. Module Ownership

| Member | Module |
| ------ | -------------------------------- |
| 1      | ML + Risk |
| 2      | Computer Vision |
| 3      | GIS + Data |
| 4      | RAG + NLP |
| 5      | Agentic AI + Relocation |
| 6      | Frontend + Backend + Integration |

---

## 4. Rules

### Before coding

1. Pull the latest changes.
2. Read `/docs/ARCHITECTURE.md`.
3. Read `/docs/API_CONTRACT.md`.
4. Read `/docs/DATABASE_SCHEMA.md`.
5. Check your module ownership.

### During development

* Stay within your assigned module.
* Do not silently change shared contracts.
* Write tests.
* Use mock data (clearly labeled) when dependent modules are unavailable.
* Keep interfaces stable.

### Before merging (NEW: contract test requirement)

* Test your module.
* **Run the shared contract test collection** (`/tests/contract/drishtisetu.postman_collection.json`, or a Schemathesis run against `/openapi.json`) against both your mock and real implementation — a PR that fails this check must not be merged.
* Test API compatibility.
* Check that existing functionality still works.
* Document important changes.
* Do not commit secrets.

---

## 5. AI Agent Rule

AI coding agents are development assistants. The human team member remains responsible for:

* Reviewing generated code
* Reviewing architecture decisions
* Checking data sources
* Checking model claims
* Testing changes
* Approving merges

AI agents must not independently redesign the project architecture.

---

## 6. Pull Request Rule

Every pull request must explain:

* What was implemented
* Files changed
* APIs affected
* Database changes
* Dependencies added
* Tests performed (including contract test result)
* Known limitations

---

## 7. Integration Checkpoints (NEW — dated)

Fill in your actual hackathon dates against these stages (mirrors `INTEGRATION_GUIDE.md`). Treat each as a hard checkpoint, not a soft target — a missed checkpoint should trigger an immediate mock fallback so downstream members are never blocked.

| Day | Stage | Owner(s) | Deliverable |
|---|---|---|---|
| Day 1 AM | Stage 1: Frontend + Backend skeleton | Member 6 | Skeleton running via Docker Compose |
| Day 1 PM | Stage 2: Mock habitation data | Member 3 (+ Member 6 integration) | `/habitations/{id}` returns mock data matching contract |
| Day 2 AM | Stage 3: Mock risk engine | Member 1 | `/risk/analyze` + `/risk/explain` return mock but contract-valid data |
| Day 2 PM | Stage 4: Mock relocation recommendation | Member 5 | `/relocation/recommend` mock live |
| Day 3 AM | Stage 5: GIS map layers | Member 3 | Map renders real/pilot-district layers |
| Day 3 PM | Stage 6: Real ML risk engine | Member 1 | Documented formula replaces mock |
| Day 4 AM | Stage 7: Real CV module | Member 2 | Real/fine-tuned model replaces mock |
| Day 4 PM | Stage 8: RAG retrieval | Member 4 | Real retrieval + insufficient-evidence path |
| Day 5 AM | Stage 9: Agentic decision layer | Member 5 | Full `/decision/analyze` live, capacity-safety test passing |
| Day 5 PM | Stage 10: End-to-end testing + decision_log + demo rehearsal | All | Full pipeline + Accept/Reject panel functional |

Adjust the day numbers to your actual hackathon schedule, but keep the checkpoint structure — it's what prevents the "everything integrates the night before" failure mode.
