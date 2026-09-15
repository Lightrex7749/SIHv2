"""
DrishtiSetu RAG/NLP module — Generation.

Two generation modes:

  * "extractive" (default, always available offline): composes the answer directly
    from the retrieved chunks' own sentences plus a one-line synthesis lead-in. No
    external LLM call, no network dependency — safe to run in tonight's sandboxed
    build environment and safe to demo without an API key.
  * "llm" (optional, pluggable): if an Anthropic API key is present in the
    environment (ANTHROPIC_API_KEY), retrieved chunks are passed to the model as
    fixed context with an instruction to answer ONLY from that context and to say
    so if the context is insufficient. This matches ARCHITECTURE.md's "AI: LLM
    accessed through configurable environment variables" line. This mode was not
    exercised tonight (no outbound network in the build sandbox) — see
    tests/test_rag.py for a mocked test of this path.

Either mode is required to: retrieve evidence before answering, provide source
metadata, avoid unsupported factual claims, and return the exact
`evidence_sufficient: false` contract response when retrieval confidence is below
threshold — never a confident-sounding guess assembled from unrelated chunks.
"""

import os
import re

INSUFFICIENT_EVIDENCE_ANSWER = (
    "Insufficient evidence was retrieved from the available knowledge base to "
    "answer this question reliably."
)


def _first_sentences(text, max_sentences=2):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:max_sentences]).strip()


def generate_extractive(query, chunks):
    """Compose an answer from the top retrieved chunks' own text (no paraphrase-by-LLM)."""
    parts = []
    for chunk in chunks:
        snippet = _first_sentences(chunk["text"], max_sentences=3)
        parts.append(f"From {chunk['title']} ({chunk['section_title']}): {snippet}")
    answer = " ".join(parts)
    return answer


def generate_llm(query, chunks):
    """
    Optional LLM-backed generation path. Requires ANTHROPIC_API_KEY in the
    environment; raises RuntimeError otherwise so callers fall back to extractive
    mode explicitly rather than silently degrading.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set — LLM generation mode is unavailable in this "
            "environment. Use generate_extractive() instead, or set the key."
        )
    try:
        import anthropic  # noqa: F401  (import here so the module has no hard dependency)
    except ImportError as exc:
        raise RuntimeError(
            "anthropic package not installed — LLM generation mode is unavailable."
        ) from exc

    context = "\n\n".join(
        f"[Source: {c['title']}, section '{c['section_title']}']\n{c['text']}" for c in chunks
    )
    system_prompt = (
        "Answer the question using ONLY the provided source excerpts. "
        "If the excerpts do not contain enough information to answer reliably, say so "
        "plainly rather than guessing. Do not invent citations, page numbers, or facts "
        "not present in the excerpts."
    )
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {query}"}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def generate_answer(query, chunks, evidence_sufficient, mode="extractive"):
    """
    Top-level entry point matching the POST /api/v1/rag/query contract shape.
    Returns (answer_text, sources_list, evidence_sufficient_bool).
    """
    if not evidence_sufficient:
        return INSUFFICIENT_EVIDENCE_ANSWER, [], False

    if mode == "llm":
        answer = generate_llm(query, chunks)
    else:
        answer = generate_extractive(query, chunks)

    sources = [
        {"title": c["title"], "source": c["source"], "page": c["page"]} for c in chunks
    ]
    return answer, sources, True
