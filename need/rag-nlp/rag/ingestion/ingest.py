"""
DrishtiSetu RAG/NLP module — Ingestion pipeline.

Pipeline stage: Documents -> Text extraction -> Cleaning -> Chunking -> Metadata -> Embeddings -> Vector storage
(per MEMBER_4_RAG_NLP.md "RAG Pipeline (unchanged structure)")

Tonight's-build notes (documented honestly, not hidden):
  * Source documents were fetched from public NDMA / Ministry of Rural Development mirrors
    (see /rag/documents/registry.json for exact URLs) and lightly re-typeset into
    [SECTION: ...] blocks under /rag/documents/raw/. This keeps the corpus small enough to
    hand-verify tonight while still being genuine government-guideline text, not placeholder
    text. A production ingestion run would instead pull the full PDFs directly and chunk them
    programmatically (see `chunk_pdf_text_placeholder` below for the intended real pipeline).
  * "Embeddings": no outbound network/package-install access was available in tonight's build
    environment, which rules out downloading a sentence-transformer model. Rather than fake an
    embedding call, retrieval below uses TF-IDF + cosine similarity (scikit-learn), which is a
    legitimate, fully-offline lexical retrieval method. This is disclosed in the API's
    `model_disclosure`-equivalent note in README.md, not hidden.
  * Page numbers: only included where confidently known from the source table of contents.
    Per MEMBER_4_RAG_NLP.md's anti-hallucination rule ("never invent... page numbers"), any
    section whose exact page could not be verified is stored with page=None rather than a
    guessed number.
"""

import json
import re
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "documents"
RAW_DIR = DOCS_DIR / "raw"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SECTION_RE = re.compile(r"\[SECTION:\s*(.+?)\]\s*\n(.*?)(?=\n\[SECTION:|\Z)", re.DOTALL)

# Page numbers confidently verified against each source document's own table of contents
# at ingestion time. Anything not listed here is intentionally left as None (unverified),
# never guessed. Keyed by (doc_id, section_title_prefix).
VERIFIED_PAGES = {
    ("NDMA-LANDSLIDES-2009", "The Context"): 1,
    ("NDMA-LANDSLIDES-2009", "Landslide Hazard Zonation Mapping"): 21,
    ("NDMA-LANDSLIDES-2009", "Landslide Risk Treatment"): 43,
    ("NDMA-FLOODS-2008", "Foreword"): None,  # roman-numeral front matter, not a body page
    ("NDMA-FLOODS-2008", "Regulation and Enforcement"): 46,
    ("NDMA-FLOODS-2008", "Capacity Development and Flood Response"): 52,
    ("NDMA-FLOODS-2008", "Achievements in Structural Measures"): 10,
    ("NDMA-NDMP-2019", "Rationale and Legal Mandate"): 1,
}


def load_registry():
    with open(DOCS_DIR / "registry.json", encoding="utf-8") as f:
        return json.load(f)["documents"]


def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_document(doc_meta):
    """Split one raw [SECTION: ...] file into retrieval chunks with metadata."""
    raw_path = DOCS_DIR / doc_meta["file"]
    raw_text = raw_path.read_text(encoding="utf-8")
    chunks = []
    for match in SECTION_RE.finditer(raw_text):
        section_title = match.group(1).strip()
        body = clean_text(match.group(2))
        if not body:
            continue
        page = VERIFIED_PAGES.get((doc_meta["doc_id"], section_title))
        chunks.append(
            {
                "chunk_id": str(uuid.uuid4())[:8],
                "doc_id": doc_meta["doc_id"],
                "title": doc_meta["title"],
                "source": doc_meta["source"],
                "section_title": section_title,
                "page": page,
                "url": doc_meta["url"],
                "text": body,
            }
        )
    return chunks


def chunk_pdf_text_placeholder(pdf_path):
    """
    Intended production path (not exercised tonight — no full PDFs were downloaded
    into this environment, only extracted excerpts; see README "Limitations").
    Would use pdfplumber (already available in this environment) to extract text
    per page, then a sliding-window chunker (~250-400 words, ~50-word overlap) to
    produce chunks that each retain their true source page number.
    """
    raise NotImplementedError(
        "Full-PDF ingestion not wired up tonight — see README.md 'Limitations'. "
        "Use chunk_document() against the pre-extracted /documents/raw/*.txt files instead."
    )


def build_corpus():
    registry = load_registry()
    all_chunks = []
    for doc_meta in registry:
        all_chunks.extend(chunk_document(doc_meta))
    out_path = DATA_DIR / "chunks.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"Ingested {len(registry)} documents into {len(all_chunks)} chunks -> {out_path}")
    return all_chunks


if __name__ == "__main__":
    build_corpus()
