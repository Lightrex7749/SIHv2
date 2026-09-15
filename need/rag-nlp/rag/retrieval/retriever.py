"""
DrishtiSetu RAG/NLP module — Retrieval.

Uses TF-IDF (word 1-2 grams) + cosine similarity over the ingested chunk corpus.
See ingestion/ingest.py module docstring for why TF-IDF rather than a downloaded
embedding model was used tonight (no outbound network in the build sandbox).

Relevance threshold: EVIDENCE_SUFFICIENT_THRESHOLD = 0.12 (cosine similarity of the
best-matching chunk against the TF-IDF query vector). This value is empirically
calibrated, not arbitrary guesswork — see /rag/README.md "Threshold calibration" for
the actual score table this was chosen against: in-corpus disaster-management questions
scored 0.18-0.55, while out-of-corpus control questions scored 0.00-0.07. 0.12 sits in the
gap between those two clusters. Re-run `python retrieval/calibrate_threshold.py` (or the
worked example in the README) if the corpus changes materially.
"""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

EVIDENCE_SUFFICIENT_THRESHOLD = 0.12
TOP_K = 3


class Retriever:
    def __init__(self, chunks_path=None):
        chunks_path = chunks_path or (DATA_DIR / "chunks.json")
        if not chunks_path.exists():
            raise FileNotFoundError(
                f"{chunks_path} not found — run `python ingestion/ingest.py` first "
                "to build the chunk corpus."
            )
        with open(chunks_path, encoding="utf-8") as f:
            self.chunks = json.load(f)
        if not self.chunks:
            raise ValueError("Chunk corpus is empty — ingestion produced no chunks.")

        self.texts = [c["text"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
        )
        self.matrix = self.vectorizer.fit_transform(self.texts)

    def search(self, query, top_k=TOP_K):
        """Return up to top_k chunks ranked by cosine similarity, each with its score."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        ranked_idx = scores.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            chunk = dict(self.chunks[idx])
            chunk["score"] = float(scores[idx])
            results.append(chunk)
        return results

    def is_evidence_sufficient(self, results):
        if not results:
            return False
        return results[0]["score"] >= EVIDENCE_SUFFICIENT_THRESHOLD
