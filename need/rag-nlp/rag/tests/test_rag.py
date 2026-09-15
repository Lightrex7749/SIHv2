"""
DrishtiSetu RAG/NLP module — test suite.

Uses the standard library's unittest rather than pytest, since pytest was not
installable in tonight's sandboxed build environment (no outbound network — see
README.md "Limitations"). Run with:
    python -m unittest discover -s tests -v
from the /rag directory.

Covers, per MEMBER_4_RAG_NLP.md "TESTING": document ingestion, chunking, metadata,
retrieval, no-result query (asserts evidence_sufficient: false + empty/minimal
sources), source attribution, malformed document, empty question, mock query.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.ingest import build_corpus, chunk_document, load_registry
from retrieval.retriever import EVIDENCE_SUFFICIENT_THRESHOLD, Retriever
from generation.generator import INSUFFICIENT_EVIDENCE_ANSWER, generate_answer
from api.handler import handle_rag_query


class TestIngestion(unittest.TestCase):
    def test_registry_loads_and_documents_exist_on_disk(self):
        registry = load_registry()
        self.assertGreaterEqual(len(registry), 3, "brief requires 3-5 real documents")
        base = Path(__file__).resolve().parent.parent / "documents"
        for doc in registry:
            self.assertTrue((base / doc["file"]).exists(), f"missing {doc['file']}")
            for required_field in ("doc_id", "title", "source", "url"):
                self.assertIn(required_field, doc)

    def test_chunking_produces_nonempty_chunks_with_metadata(self):
        registry = load_registry()
        chunks = chunk_document(registry[0])
        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertTrue(c["text"].strip())
            self.assertEqual(c["doc_id"], registry[0]["doc_id"])
            self.assertIn("section_title", c)
            # page is either a verified int or explicitly None — never a fabricated guess
            self.assertTrue(c["page"] is None or isinstance(c["page"], int))

    def test_chunk_document_handles_malformed_document_gracefully(self):
        """A doc whose raw file has no [SECTION: ...] markers should yield zero
        chunks, not crash — this is the 'malformed document' test case."""
        malformed_meta = {
            "doc_id": "MALFORMED-TEST",
            "title": "Malformed",
            "source": "test",
            "url": "http://example.invalid",
            "file": "raw/__malformed_test.txt",
        }
        base = Path(__file__).resolve().parent.parent / "documents"
        (base / malformed_meta["file"]).write_text("no section markers here at all")
        try:
            chunks = chunk_document(malformed_meta)
            self.assertEqual(chunks, [])
        finally:
            (base / malformed_meta["file"]).unlink()

    def test_build_corpus_writes_chunks_json(self):
        chunks = build_corpus()
        self.assertGreater(len(chunks), 0)


class TestRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_corpus()
        cls.retriever = Retriever()

    def test_in_corpus_query_returns_sufficient_evidence(self):
        results = self.retriever.search(
            "What factors should be considered when planning relocation from a "
            "landslide-prone habitation?"
        )
        self.assertTrue(self.retriever.is_evidence_sufficient(results))
        self.assertGreater(results[0]["score"], EVIDENCE_SUFFICIENT_THRESHOLD)

    def test_out_of_corpus_query_returns_insufficient_evidence(self):
        """The demo query identified for the team's insufficient-evidence moment
        (see README.md 'Insufficient-evidence demo query')."""
        results = self.retriever.search(
            "What is the sediment transport model used for coastal erosion "
            "prediction on the Konkan coast?"
        )
        self.assertFalse(self.retriever.is_evidence_sufficient(results))

    def test_source_attribution_present_on_results(self):
        results = self.retriever.search("landslide hazard zonation mapping")
        for r in results:
            self.assertIn("title", r)
            self.assertIn("source", r)
            self.assertIn("url", r)


class TestGeneration(unittest.TestCase):
    def test_insufficient_evidence_shape_matches_contract(self):
        answer, sources, evidence_sufficient = generate_answer("irrelevant query", [], False)
        self.assertEqual(answer, INSUFFICIENT_EVIDENCE_ANSWER)
        self.assertEqual(sources, [])
        self.assertFalse(evidence_sufficient)


class TestApiHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_corpus()

    def test_empty_question_raises(self):
        with self.assertRaises(ValueError):
            handle_rag_query("")

    def test_mock_mode_found_path_matches_contract_shape(self):
        result = handle_rag_query(
            "What should be considered when relocating a landslide habitation?",
            mode="mock",
        )
        self.assertIn("answer", result)
        self.assertIn("sources", result)
        self.assertTrue(result["evidence_sufficient"])
        self.assertEqual(len(result["sources"]), 1)
        self.assertIn("page", result["sources"][0])

    def test_mock_mode_not_found_path_matches_contract_shape(self):
        result = handle_rag_query("something totally unrelated to disasters", mode="mock")
        self.assertFalse(result["evidence_sufficient"])
        self.assertEqual(result["sources"], [])
        self.assertEqual(
            result["answer"],
            "Insufficient evidence was retrieved from the available knowledge base "
            "to answer this question reliably.",
        )

    def test_real_mode_end_to_end_no_result_query(self):
        result = handle_rag_query(
            "What is the sediment transport model used for coastal erosion "
            "prediction on the Konkan coast?",
            mode="real",
        )
        self.assertFalse(result["evidence_sufficient"])
        self.assertEqual(result["sources"], [])

    def test_real_mode_end_to_end_found_query(self):
        result = handle_rag_query(
            "What is the vision of the National Disaster Management Plan 2019?",
            mode="real",
        )
        self.assertTrue(result["evidence_sufficient"])
        self.assertGreater(len(result["sources"]), 0)
        for s in result["sources"]:
            self.assertIn("title", s)
            self.assertIn("source", s)


if __name__ == "__main__":
    unittest.main()
