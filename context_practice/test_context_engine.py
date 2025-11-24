# test_context_engine.py

import pytest
from context_engine import Document, SearchResult, tokenize, build_index, search, precision_at_k


def sample_docs():
    return [
        Document(
            id="doc1",
            title="Intro to Retrieval-Augmented Generation",
            body="RAG connects LLMs to external knowledge bases.",
            tags=["rag", "llm"],
            access_level=1,
        ),
        Document(
            id="doc2",
            title="Context engineering best practices",
            body="Chunking, retrieval, and prompting work together.",
            tags=["context", "best-practices"],
            access_level=2,
        ),
        Document(
            id="doc3",
            title="Private customer runbook",
            body="Contains sensitive onboarding steps for enterprise customers.",
            tags=["internal", "runbook"],
            access_level=3,
        ),
    ]


def test_tokenize_basic():
    text = "Hello, World! 123"
    assert tokenize(text) == ["hello", "world", "123"]


def test_tokenize_strips_punctuation_and_lowercases():
    text = "RAG: Retrieval-Augmented   Generation!!!"
    tokens = tokenize(text)
    assert tokens == ["rag", "retrieval", "augmented", "generation"]


def test_build_index_has_expected_terms_and_counts():
    idx = build_index(sample_docs())
    # spot-check some terms
    assert "rag" in idx
    assert "context" in idx

    # "RAG connects LLMs to external knowledge bases."
    # So "rag" appears once in doc1.
    assert idx["rag"]["doc1"] == 1

    # "customers." should become token "customers" in doc3 body
    assert idx["customers"]["doc3"] == 1


def test_search_simple_query_all_access():
    docs = sample_docs()
    idx = build_index(docs)
    results = search(idx, docs, query="retrieval rag")

    # doc1 should be the best match (contains both retrieval and rag)
    assert results
    assert results[0].doc_id == "doc1"
    assert results[0].score > 0

    # doc2 mentions retrieval in body so it should appear too
    ids = [r.doc_id for r in results]
    assert "doc2" in ids


def test_search_respects_access_level():
    docs = sample_docs()
    idx = build_index(docs)

    # user with access_level 1 shouldn't see doc3 (access_level=3)
    results = search(idx, docs, query="customer customers", user_access_level=1)
    ids = [r.doc_id for r in results]
    assert "doc3" not in ids

    # user with higher access can see doc3
    results_high = search(idx, docs, query="customer customers", user_access_level=3)
    ids_high = [r.doc_id for r in results_high]
    assert "doc3" in ids_high


def test_search_max_results_and_sorting():
    docs = sample_docs()
    idx = build_index(docs)

    results = search(
        idx,
        docs,
        query="customers customer enterprise private",
        max_results=1,
        user_access_level=3,
    )

    # only first result should be returned
    assert len(results) == 1
    # since all signals point to doc3, it should come first
    assert results[0].doc_id == "doc3"


def test_precision_at_k_basic():
    retrieved = [
        SearchResult(doc_id="doc1", score=1.0),
        SearchResult(doc_id="doc2", score=0.5),
        SearchResult(doc_id="doc3", score=0.1),
    ]
    gold = {"doc1", "doc3"}

    # At k=1, only doc1 considered, and it's relevant
    assert precision_at_k(gold, retrieved, k=1) == pytest.approx(1.0)

    # At k=2, doc1 relevant, doc2 not
    assert precision_at_k(gold, retrieved, k=2) == pytest.approx(0.5)

    # At k=3, two relevant out of 3 considered
    assert precision_at_k(gold, retrieved, k=3) == pytest.approx(2 / 3)


def test_precision_at_k_edge_cases():
    # k == 0
    retrieved = [SearchResult(doc_id="doc1", score=1.0)]
    gold = {"doc1"}
    assert precision_at_k(gold, retrieved, k=0) == 0.0

    # empty retrieved list
    assert precision_at_k(gold, [], k=3) == 0.0

    # k > len(retrieved): denominator still k
    assert precision_at_k(gold, retrieved, k=5) == pytest.approx(1 / 5)
