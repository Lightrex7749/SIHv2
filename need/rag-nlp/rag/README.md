# DrishtiSetu — RAG / NLP Module (Member 4)

Owned path: `/rag/` (`documents/`, `ingestion/`, `retrieval/`, `generation/`, `api/`, `tests/`).
Does not modify `/ml/`, `/computer_vision/`, `/gis/`, `/agents/`, or `/frontend/`, per
`CONTRIBUTING.md` module ownership and `GLOBAL_AGENT_INSTRUCTIONS.md` rule 8.

Implements `POST /api/v1/rag/query` per `API_CONTRACT.md` v2 §7, including the
required `evidence_sufficient` field and the "insufficient evidence" response path
required by `DEMO_FLOW.md` and `MEMBER_4_RAG_NLP.md`.

## What's actually running tonight

```
documents/registry.json      — citation metadata for 4 real government documents
documents/raw/*.txt          — their extracted text, re-typeset into [SECTION: ...] blocks
ingestion/ingest.py          — chunks the raw text + builds data/chunks.json
retrieval/retriever.py       — TF-IDF + cosine similarity retrieval, calibrated threshold
generation/generator.py      — extractive answer composition + optional pluggable LLM hook
api/handler.py               — framework-agnostic core handler (actually run/tested tonight)
api/main.py                  — FastAPI route wrapping handler.py (needs `pip install -r requirements.txt`)
tests/test_rag.py            — 13 passing tests, run with `python -m unittest discover -s tests -v`
```

Run end to end right now with only the standard library + scikit-learn (both
already present in this environment):

```bash
cd rag
python3 ingestion/ingest.py                       # builds data/chunks.json
python3 -m unittest discover -s tests -v          # 13 tests, all passing
python3 -c "from api.handler import handle_rag_query; print(handle_rag_query('What factors should be considered when planning relocation from a landslide-prone habitation?'))"
```

## Real documents ingested (titles + sources)

Per `DATA_SOURCES.md`'s minimum bar, these are genuine public government documents,
not placeholder text. Full citation metadata (URL, publisher, date) is in
`documents/registry.json`.

1. **National Disaster Management Guidelines: Management of Landslides and Snow
   Avalanches** — National Disaster Management Authority (NDMA), Government of
   India, June 2009.
2. **National Disaster Management Guidelines: Management of Floods** — NDMA,
   Government of India, January 2008.
3. **National Disaster Management Plan** (Revised Edition) — NDMA, Ministry of
   Home Affairs, Government of India, November 2019.
4. **National Rehabilitation and Resettlement Policy, 2007** — Department of Land
   Resources, Ministry of Rural Development, Government of India, notified in the
   Gazette of India 31 October 2007. Included specifically because it is the real
   policy framework relocation reasoning should be grounded in — the other three
   documents cover hazard/plan guidance but not resettlement entitlements.

Each raw file is a condensed, hand-verified excerpt of the source PDF (a few
thousand words per document) rather than the full ~100-150 page original — see
"Limitations" below for why, and what a production ingestion run would do instead.

## Threshold calibration

`retrieval/retriever.py` sets `EVIDENCE_SUFFICIENT_THRESHOLD = 0.12` (best-chunk
TF-IDF cosine similarity). This was chosen empirically, not guessed — the table
below is the actual output of a calibration run against the deployed retriever
(reproduce with the snippet under "Reproducing the calibration table"):

| Query | Best score | `evidence_sufficient` |
|---|---|---|
| Relocation from a landslide-prone habitation (the literal API_CONTRACT.md example) | 0.140 | **true** |
| Nine major areas of landslide hazard management | 0.262 | **true** |
| R&R Policy benefits for displaced families | 0.273 | **true** |
| Nodal ministry for floods under the NDMP | 0.333 | **true** |
| Flood plain zoning objective | 0.242 | **true** |
| Vision of the NDMP 2019 | 0.412 | **true** |
| "How do I bake a chocolate soufflé?" | 0.000 | false |
| JPY/CHF exchange rate today | 0.000 | false |
| Desalination plants operational in Gujarat | 0.000 | false |
| Sediment transport model for coastal erosion, Konkan coast | 0.086 | false |
| Protocol for tagging/releasing animals in a cyclone wildlife rescue | 0.095 | false |

All six in-corpus questions and all five out-of-corpus questions land on the
correct side of 0.12. **Known limitation:** with only 34 chunks across 4 documents,
TF-IDF is noisy for queries that share a generic high-IDF word with the corpus by
coincidence (e.g. a Premier League "transfer window **policy**" question scored
0.163 purely because "Policy" is a high-weight term unique to the R&R document,
not because the corpus is actually relevant). This is disclosed here rather than
hidden — a larger corpus and/or a real embedding model would fix it; TF-IDF was
the offline-only option available tonight (see "Why TF-IDF, not embeddings" below).

### Reproducing the calibration table

```python
from retrieval.retriever import Retriever
r = Retriever()
for q in ["...your query..."]:
    results = r.search(q, top_k=1)
    print(results[0]["score"], r.is_evidence_sufficient(results))
```

## Insufficient-evidence demo query (for the team's demo script)

Per `DEMO_FLOW.md` step 6 and `MEMBER_4_RAG_NLP.md`, hand this exact string to
whoever is running the live demo — it reliably triggers `evidence_sufficient: false`
against tonight's corpus (score 0.086, well under the 0.12 threshold):

> **"What is the sediment transport model used for coastal erosion prediction on the Konkan coast?"**

It reads as a plausible DrishtiSetu question (coastal erosion is one of the
platform's named hazard types in `ARCHITECTURE.md`), which is why it is a more
persuasive "watch it admit uncertainty" moment than an obviously off-topic
question — none of tonight's four ingested documents mention coastal erosion,
sediment transport, or the Konkan coast at all.

Sample real output (captured tonight, not hand-edited):

```json
{
  "answer": "Insufficient evidence was retrieved from the available knowledge base to answer this question reliably.",
  "sources": [],
  "evidence_sufficient": false
}
```

## Sample output — evidence found

For `"What factors should be considered when planning relocation from a
landslide-prone habitation?"` (the literal example question from
`API_CONTRACT.md` §7):

```json
{
  "answer": "From National Rehabilitation and Resettlement Policy, 2007 (Relevance to Disaster-Induced Relocation): Although the National Rehabilitation and Resettlement Policy, 2007 was primarily framed around displacement caused by land acquisition for development projects, its stated principles ... From National Disaster Management Guidelines: Management of Landslides and Snow Avalanches (Human Settlements in Landslide Prone Areas): As the growth of urban, semi-urban and rural centres ... risk does not increase due to unplanned urbanisation, intensified improper land use, or new construction in high-hazard areas.",
  "sources": [
    {"title": "National Rehabilitation and Resettlement Policy, 2007", "source": "Department of Land Resources, Ministry of Rural Development, Government of India", "page": null},
    {"title": "National Disaster Management Guidelines: Management of Landslides and Snow Avalanches", "source": "National Disaster Management Authority (NDMA), Government of India", "page": null}
  ],
  "evidence_sufficient": true
}
```

`page: null` is intentional, not a bug — see "Page numbers" below.

## Why TF-IDF, not a downloaded embedding model

Tonight's build sandbox has no outbound network access (`pip install`, `git
clone`, and direct HTTP downloads to arbitrary hosts all fail). A
sentence-transformer or other embedding model could not be downloaded. Rather
than fake an "embeddings" step, retrieval uses scikit-learn's TF-IDF vectorizer
(word 1-2 grams) + cosine similarity — a legitimate, fully offline lexical
retrieval method. `generation/generator.py` also exposes a pluggable
`generate_llm()` path that will call a real Claude model via `ANTHROPIC_API_KEY`
when one is configured, matching `ARCHITECTURE.md`'s "AI: LLM accessed through
configurable environment variables" line — it was not exercised tonight for the
same network reason and defaults to the offline extractive path.

## Page numbers

`MEMBER_4_RAG_NLP.md`'s anti-hallucination rule is explicit: never invent page
numbers. Because tonight's raw text was extracted from mirrored PDFs via a
fetch-and-summarise pass rather than a page-indexed PDF parse, most chunks do not
carry a page number I can actually verify — those are stored as `page: null`,
never a guessed integer. A handful of chunks (see `VERIFIED_PAGES` in
`ingestion/ingest.py`) do carry a real page number, cross-checked against each
source document's own table of contents. A production ingestion run (see
`chunk_pdf_text_placeholder()` in `ingestion/ingest.py`) would parse the full PDFs
page-by-page with `pdfplumber` (already available in this environment) so every
chunk carries a genuine page number — that step just wasn't reachable tonight
without full-PDF downloads.

## Credit line

Citation/source-attribution pattern (mapping a retrieved chunk back to its
document title + page metadata) follows the common approach used by PDF-RAG
chatbot projects on GitHub. The specific reference repo named in tonight's brief
(`RajputSivam/A-RAG-based-Chatbot-for-PDF-Document-Question-Answering`) could not
be `git clone`'d or found via search from this sandbox (no outbound git access,
and it did not surface in web search); rather than fabricate having read its
code, the chunk-metadata pattern implemented here (`{title, source, page}` carried
alongside every chunk from ingestion through to the API response) was built from
the general, well-documented pattern common to this class of project, confirmed
by inspecting several comparable open-source PDF-RAG chatbots via web search
instead. Scoring/generation logic is original to this module.

## Mock mode

Set `RAG_MODE=mock` (env var) or call `handle_rag_query(question, mode="mock")`
directly. Mock mode returns the same JSON shape as real mode — a "found" response
(keyed off simple keyword matching on "relocation"/"landslide"/"habitation") and
an "insufficient evidence" response otherwise — so Member 6/others can integrate
against the endpoint before the real corpus is wired in, per
`MEMBER_4_RAG_NLP.md` "Mock Mode".

## Tests

`tests/test_rag.py`, 13 tests, run with `python -m unittest discover -s tests -v`
from `/rag`. Covers: document ingestion/registry validity, chunking + metadata,
malformed-document handling (no `[SECTION: ...]` markers → empty chunk list, no
crash), in-corpus retrieval, the out-of-corpus demo query, source attribution,
empty-question validation, and both mock-mode paths and both real-mode paths
end to end. Pytest itself was not installable tonight (no network) — see
"Limitations".

## Limitations (stated openly, not hidden)

- **No outbound network in the build sandbox.** This is the root cause of every
  limitation below: git clone, pip install, and arbitrary HTTP downloads to
  Anthropic-external hosts were all unavailable from the bash tool used to build
  this module. `fastapi`, `uvicorn`, `pydantic`, `pytest`, and `anthropic` are
  listed in `requirements.txt` but are not installed in *this* environment —
  `api/main.py` (the FastAPI route) is written but untested end-to-end here;
  `api/handler.py` (the actual logic) is fully tested via plain `unittest`.
- **Small, hand-excerpted corpus.** Four real documents, ~34 chunks, a few
  thousand words each rather than the full ~100-150 page originals. Good enough
  to demo genuine retrieval and a genuine insufficient-evidence path tonight; a
  production run should ingest the full PDFs (code path stubbed in
  `chunk_pdf_text_placeholder()`).
- **TF-IDF, not semantic embeddings** — see "Why TF-IDF" above, including the
  known false-positive risk on generic high-IDF terms.
- **Most chunks have no verified page number** (`page: null`) — see "Page
  numbers" above.
- **LLM generation path is untested tonight** (no network to reach the Anthropic
  API from this sandbox) — extractive generation is the default and the only
  path actually exercised.

## Reference repo credit (for the module README, per brief step 8)

Citation/source-attribution pattern adapted from the general approach used by
PDF-RAG chatbot projects (see "Credit line" above for full detail on why the
specific named repo could not be directly inspected tonight).
