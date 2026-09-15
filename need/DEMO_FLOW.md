# Demonstration Flow (v2)

## Scenario

The authority selects a vulnerable habitation on the GIS map. **Use a real, seeded pilot district for this walkthrough — not a purely synthetic example.**

---

### Step 1 — GIS Map

Display: habitations, hazard zones, Red Zones, candidate relocation sites, **land-use conflict overlay (NEW)**.

---

### Step 2 — Habitation Selection

Show: population, hazard exposure, historical disaster events, vulnerability, risk score.

---

### Step 3 — AI Risk Analysis

Display: hazard score, vulnerability score, overall risk, risk level, relocation priority.

**NEW — click "Why this score?"** to open the explainability drawer (`/risk/explain`), showing the per-factor breakdown. *This is your strongest technical credibility moment — do not skip it in the demo.*

---

### Step 4 — Computer Vision

Display an example disaster image (ideally a before/after satellite patch) and show detected visual hazard indicators, **including the `model_disclosure` text (NEW)** so the claim is honest and specific rather than an unqualified confidence number.

---

### Step 5 — Relocation Analysis

Display candidate sites with: distance/accessibility, residual hazard, estimated capacity, healthcare access, water access, school access, suitability score, **land-use conflict flag (NEW)**.

---

### Step 6 — RAG

Show evidence retrieved from authoritative disaster-management documents.

**NEW — run a second, deliberately obscure query** that has no good match in the knowledge base, and show the system respond with `evidence_sufficient: false` rather than guessing. *This "watch it admit uncertainty" moment is more persuasive to judges than a perfect answer.*

---

### Step 7 — Agentic Decision

The Decision Agent combines ML, CV, GIS, population vulnerability, site capacity, RAG evidence, and generates an explainable recommendation, **including an estimated relocation cost where a benchmark is available (NEW)**.

**NEW — capacity-safety demo:** show (in code or via a prepared test case) a scenario where population exceeds site capacity, and demonstrate that the system reports `capacity_sufficient: false` even if prompted to say otherwise — proving the LLM cannot override the deterministic math.

---

### Step 8 — Authority Dashboard

Final output:

```text
RISK LEVEL: HIGH
RELOCATION PRIORITY: IMMEDIATE
RECOMMENDED SITE: Candidate Site A
LAND-USE CONFLICT: None detected
CAPACITY: SUFFICIENT (1250 of 1800)
SUITABILITY: 84.5%
ESTIMATED COST: ₹6.25 Cr (illustrative, see cost_basis)

KEY REASONS:
• High multi-hazard exposure
• High population vulnerability
• Candidate site has sufficient estimated capacity
• Better accessibility
• Lower residual hazard
• No land-use conflict on candidate site

EVIDENCE:
[Source 1]
[Source 2]
```

---

### Step 9 — Authority Action (NEW, do not skip)

Demonstrate the Accept / Reject / Defer panel: authority selects "Accepted," adds a note, submits. **Reload the page and show the entry persisted in the decision log** — this is the step that proves the system is a decision-support tool with accountability, not an autonomous black box.

---

The system provides decision support; authorized authorities make the final decision, and that decision is permanently recorded.
