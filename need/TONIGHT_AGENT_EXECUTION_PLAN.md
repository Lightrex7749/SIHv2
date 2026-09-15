# DrishtiSetu — Tonight's Agent Execution Plan

**How to use this file:** Each section below is a self-contained prompt.
Copy the ENTIRE contents of a section (including the code block) and paste
it as the first message to that member's AI coding agent (Claude Code, etc.),
run inside their branch of the repo. The agent will pull the reference repo,
extract the useful part, delete the reference clone, and build the real
module against your existing v2 docs — in that order.

**Golden rule for tonight:** Reference repos are for extracting *patterns and
working code snippets*, never for wholesale copy-paste into your submission.
Always add a one-line credit. This keeps you honest for judges AND makes the
code you actually understand and can explain on stage.

---

## MEMBER 6 — Run this FIRST (nothing else can start until this is done)

```
You are Member 6 (Full-Stack + Integration) on the DrishtiSetu team.
Read /docs/MEMBER_6_FULLSTACK_INTEGRATION.md and /docs/API_CONTRACT.md fully
before doing anything else.

STEP 1 — Pull a reference for the mock-fallback pattern:
  git clone --depth 1 https://github.com/Memeetesh/AI-disaster-managementandresponse-platform reference/disaster-platform

STEP 2 — Inspect ONLY reference/disaster-platform/backend/ for how they
structure: (a) FastAPI route organization, (b) SQLAlchemy + GeoAlchemy2
models, (c) their "real -> cache -> demo data" degrade pattern for external
integrations. Do not copy their business logic or database schema — ours is
already defined in /docs/DATABASE_SCHEMA.md and must not change.

STEP 3 — Delete reference/disaster-platform once you've extracted the
pattern ideas (rm -rf reference/disaster-platform) so it never ends up in
our submission or git history.

STEP 4 — Build our actual backend skeleton from scratch, following OUR
contract exactly:
  - FastAPI app with all endpoints in /docs/API_CONTRACT.md (v2), each
    returning hardcoded/mocked responses that exactly match the documented
    JSON shape, including the new /risk/explain, /decision/log (POST+GET)
  - PostgreSQL + PostGIS via docker-compose, using OUR schema in
    /docs/DATABASE_SCHEMA.md (including decision_log, land_use_zones)
  - Apply their "real -> cache -> demo data" degrade pattern to how each
    endpoint handles a missing/incomplete downstream module: never crash,
    always fall back to labeled mock data
  - React + Leaflet frontend skeleton with routing for each dashboard panel
    named in the doc (map, risk panel, relocation panel, evidence panel,
    Authority Action panel)

STEP 5 — Push this skeleton immediately so the other 5 members can start
building against a live mock API. This is the most time-critical step of
the entire night — do it before polishing anything.

STEP 6 — Set up /tests/contract/ with a minimal Postman/Newman collection
or Schemathesis config that checks each endpoint returns the required
fields from API_CONTRACT.md v2. Doesn't need to be exhaustive tonight —
just enough to catch an obviously broken/renamed field.

Report back: what's running, on what port, and exact curl examples for
each endpoint so other members can test against it immediately.
```

---

## MEMBER 1 — ML / Risk Engine

```
You are Member 1 (ML/Risk Engineer) on the DrishtiSetu team.
Read /docs/MEMBER_1_ML_RISK.md fully before doing anything else.
Wait until Member 6's backend skeleton is pushed and running, then pull latest.

STEP 1 — Pull a reference for explainable risk-scoring structure:
  git clone --depth 1 https://github.com/DISHITACHAUHAN/BHUSHAKTI-AI reference/bhushakti

STEP 2 — Inspect ONLY the backend risk-scoring + SHAP explainability code
(look for XGBoost model + SHAP usage). Extract the PATTERN of how they turn
a model's output into a per-factor explanation — not their specific weights
or feature set, which don't match our contract.

STEP 3 — Delete reference/bhushakti once you've extracted the pattern:
  rm -rf reference/bhushakti

STEP 4 — Implement calculate_hazard_score(), calculate_vulnerability_score(),
calculate_overall_risk(), classify_risk_level(), determine_relocation_priority()
using OUR documented formula in ARCHITECTURE.md section 9D. Since we don't
have time tonight to run a full AHP weighting exercise, use these starting
weights and document them AS an illustrative first pass in your README:
  hazard: rainfall 0.3, slope 0.25, elevation_stability 0.2, historical_freq 0.25
  vulnerability: population_density 0.4, infra_access 0.35, demographic 0.25
  overall: hazard 0.5, vulnerability 0.35, historical 0.15
State clearly in the README that these are a documented starting baseline,
not derived from a validated framework — honesty here is better than a
fabricated citation.

STEP 5 — Implement explain_risk_score() backing GET /api/v1/risk/explain/{id}
per API_CONTRACT.md v2 section 3A — return the weighted contribution of
each factor, not just the total.

STEP 6 — Write unit tests: low/moderate/high/critical risk cases, invalid
input, missing values, and one test asserting the explain breakdown sums
approximately to overall_score.

STEP 7 — Add a credit line to your module README: "Explainability pattern
inspired by BHUSHAKTI-AI (github.com/DISHITACHAUHAN/BHUSHAKTI-AI), scoring
logic is our own implementation."

Report back: exact API output for one sample habitation, formula used,
tests passed.
```

---

## MEMBER 2 — Computer Vision

```
You are Member 2 (Computer Vision Engineer) on the DrishtiSetu team.
Read /docs/MEMBER_2_COMPUTER_VISION.md fully before doing anything else.
Wait until Member 6's backend skeleton is pushed, then pull latest.

Given tonight's time limit, do this in two phases — get Phase 1 fully
working before attempting Phase 2.

=== PHASE 1 (REQUIRED — do this first, it alone is enough to demo) ===

Build a mock CV service that:
  - Accepts POST /api/v1/vision/analyze per API_CONTRACT.md v2
  - Returns realistic, deterministic detections (pick 3-4 fixed
    image_url -> detection mappings so the same input always gives the
    same output in the demo)
  - ALWAYS includes the model_disclosure field, worded honestly, e.g.:
    "Prototype uses a rule-based/mock detector for demo purposes. Production
    implementation would use a model fine-tuned on Sen1Floods11 (flood) and
    Landslide4Sense (landslide), both public benchmark datasets."
  - Has full unit tests and a clean mock/real interface split so Phase 2
    can slot in without changing the API

=== PHASE 2 (STRETCH — only if Phase 1 is done and tested with time left) ===

STEP 1 — Pull the pretrained flood segmentation model:
  pip install huggingface_hub --break-system-packages
  python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='ibm-nasa-geospatial/Prithvi-100M-sen1floods11', local_dir='reference/prithvi-flood')"

STEP 2 — Also pull a landslide segmentation reference for the inference
pipeline shape (not to train, just to see how they load/run a U-Net):
  git clone --depth 1 https://github.com/isaaccorley/landslide4sense reference/landslide4sense

STEP 3 — Try wiring the Prithvi model into a real inference call for flood
detection on a sample Sentinel-2 patch. This requires mmsegmentation and is
genuinely heavy to set up — if it's not working within ~1 hour, abandon it
and keep Phase 1's honest mock. A working honest mock beats a half-broken
real model on stage.

STEP 4 — If Phase 2 succeeds, update model_disclosure to reflect the real
model used, and add a credit line: "Flood detection uses IBM/NASA's
Prithvi-100M model fine-tuned on Sen1Floods11 (Apache-2.0 license)."

STEP 5 — Delete reference/prithvi-flood and reference/landslide4sense from
the repo before final commit either way (rm -rf reference/) — these are
large multi-GB downloads that should never enter your git history.

Report back: which phase you reached, exact API output, and whether
model_disclosure accurately reflects what's actually running.
```

---

## MEMBER 3 — GIS / Data

```
You are Member 3 (GIS and Data Engineer) on the DrishtiSetu team.
Read /docs/MEMBER_3_GIS_DATA.md fully before doing anything else.
Wait until Member 6's backend skeleton is pushed, then pull latest.

No repo to clone tonight — focus entirely on getting real data for ONE
pilot district, since that's the highest-leverage fix available in one
night.

STEP 1 — Pick one Indian district you can find real open data for quickly
(a well-documented one, e.g. a district in Uttarakhand or Kerala tends to
have decent public disaster-data coverage). Confirm the choice with the team.

STEP 2 — Pull real data for that district only:
  - Population: village/town-level counts from Census of India (or use
    WorldPop gridded data if Census lookup is too slow tonight)
  - Admin boundary: Survey of India / Bhuvan, or a simplified OSM boundary
    extract via Overpass API if faster
  - Roads/water/schools/hospitals: OpenStreetMap via Overpass API
    (fastest real-data source available tonight — use this as your primary)
  - Elevation/slope: if a DEM download is too slow tonight, it's
    acceptable to use SRTM data already packaged in a Python library
    (e.g. via elevation/rasterio) rather than a manual Bhuvan download

STEP 3 — Seed 5-8 habitations in this district with a MIX of real
population/location and clearly-labeled synthetic risk indicators
(source = 'SYNTHETIC_DEMO' on any field you had to invent, like exact
rainfall/slope numbers if you couldn't source them in time).

STEP 4 — Build the land_use_zones table and land-use conflict check
function ONLY if time remains after real data seeding — this is valuable
but secondary tonight. A simple ST_Intersects query against one manually-
drawn polygon (even a rough forest-boundary guess) is enough to demo the
feature; it doesn't need to be a real FSI dataset tonight.

STEP 5 — Document every real source used (with actual URLs) in
/docs/DATA_SOURCES.md immediately — don't leave this for later, it's easy
to forget which numbers were real vs invented once you're deep in code.

Report back: which district, which fields are real vs synthetic (be
precise), and API output for GET /api/v1/gis/risk-layers.
```

---

## MEMBER 4 — RAG / NLP

```
You are Member 4 (RAG + NLP Engineer) on the DrishtiSetu team.
Read /docs/MEMBER_4_RAG_NLP.md fully before doing anything else.
Wait until Member 6's backend skeleton is pushed, then pull latest.

STEP 1 — Pull a reference for the citation/source-attribution pattern:
  git clone --depth 1 https://github.com/RajputSivam/A-RAG-based-Chatbot-for-PDF-Document-Question-Answering reference/rag-pdf-chatbot

STEP 2 — Inspect ONLY their ingestion/chunking and citation-mapping logic
(how they map a retrieved chunk back to its source file + page number).
Do not copy their frontend or their specific LLM prompt wording wholesale —
adapt the pattern to our exact output contract.

STEP 3 — Delete the reference clone once extracted:
  rm -rf reference/rag-pdf-chatbot

STEP 4 — Gather 3-5 REAL public disaster-management PDFs tonight (fastest
options: NDMA guideline PDFs, or any publicly available State Disaster
Management Plan PDF you can find and download quickly). This matters more
than a large corpus — even 3 real documents beats a big pile of placeholder
text for credibility.

STEP 5 — Build the ingestion pipeline: extract text, chunk, embed (a local/
free embedding model is fine if you don't want to burn API budget tonight),
store with metadata (title, source org, page number).

STEP 6 — Implement POST /api/v1/rag/query per API_CONTRACT.md v2, including
the evidence_sufficient field. Set a concrete similarity threshold below
which you return evidence_sufficient: false and an honest "insufficient
evidence" answer — document the exact threshold value in your README.

STEP 7 — Identify ONE query against your real corpus that reliably returns
evidence_sufficient: false (e.g., ask something your 3-5 documents clearly
don't cover) and hand this exact query string to whoever is writing the
demo script — this is a required demo moment per DEMO_FLOW.md.

STEP 8 — Add a credit line to your module README crediting the citation-
pattern reference repo.

Report back: which real documents you ingested (titles + sources), the
exact insufficient-evidence demo query, and sample API output for both
paths.
```

---

## MEMBER 5 — Agentic AI + Relocation

```
You are Member 5 (Agentic AI + Relocation Engineer) on the DrishtiSetu team.
Read /docs/MEMBER_5_AGENTIC_AI.md fully before doing anything else.
Wait until Members 1, 3, and 4 have at least their mock/real endpoints
running (check with them or hit their endpoints directly), then pull latest.

No repo pull needed tonight — this module is mostly orchestration logic
specific to our contract, and no external repo maps closely enough to be
worth the time cost of adapting it.

STEP 1 — Build the Capacity Agent first, since it's the highest-priority
safety feature: implement capacity_sufficient as a pure Python boolean
function — population_to_relocate <= site_capacity * safety_margin
(use safety_margin = 0.9 as a documented starting default) — computed
BEFORE any LLM call.

STEP 2 — Write the adversarial test required by your brief: construct a
prompt that tries to get an LLM call to claim capacity is sufficient when
it isn't, and assert your API output is unaffected. This test, once
passing, is one of your best demo moments — flag it to whoever's building
the demo script.

STEP 3 — Build the Relocation Agent: rank candidate sites from Member 3's
GIS output using suitability_score, factoring in land_use_conflict if
Member 3 has that ready (fall back gracefully if not — never crash on a
missing field).

STEP 4 — Build the Decision Agent: call Member 1's risk endpoint, Member 3's
GIS endpoint, Member 4's RAG endpoint, and your own Relocation/Capacity
agents, and assemble the final /api/v1/decision/analyze response exactly
per API_CONTRACT.md v2. If a downstream module isn't ready yet, use a
documented mock matching its contract shape — don't block on it.

STEP 5 — Add estimated_cost as an OPTIONAL field: if you can quickly find
one illustrative public per-capita resettlement cost benchmark, use it and
cite it in cost_basis; if not, return null and say so honestly rather than
inventing a number — this is explicitly allowed by your brief.

STEP 6 — Set status: "PROPOSED" as the default on every new recommendation.

Report back: full sample output of /api/v1/decision/analyze end to end,
and confirmation the adversarial capacity test passes.
```

---

## Coordination notes for tonight

- **Merge order matters.** Member 6's skeleton must land first. After that,
  Members 1, 3, and 4 can work in parallel since they don't depend on each
  other. Member 5 depends on all three, so they should start with the
  Capacity Agent (self-contained) while waiting.
- **Every `reference/` folder must be deleted before the final commit.**
  Add `reference/` to `.gitignore` right now so nobody accidentally commits
  a multi-GB model checkpoint.
- **Credit lines go in each module's own README**, not a single shared file
  — this makes it obvious during Q&A which specific piece came from where.
- **Freeze features by the time from the earlier schedule (around 4:30am)**
  and move to the merge-and-rehearse phase — this plan gets you working
  code, but only rehearsal gets you a working demo.
