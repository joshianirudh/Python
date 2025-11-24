# context_engine.py

from dataclasses import dataclass
from typing import List, Dict, Set
from collections import defaultdict, Counter

@dataclass
class Document:
    """
    Simple representation of a document in a context/retrieval system.

    Fields:
      - id: unique identifier (e.g. "doc1")
      - title: short title of the document
      - body: main text content
      - tags: list of string tags (e.g. ["rag", "llm"])
      - access_level: integer representing sensitivity. Higher = more restricted.
    """
    id: str
    title: str
    body: str
    tags: List[str]
    access_level: int


@dataclass
class SearchResult:
    """
    Represents a scored search result.

    Fields:
      - doc_id: the id of the matched document
      - score: numeric relevance score (higher is better)
    """
    doc_id: str
    score: float


def tokenize(text: str) -> List[str]:
    """
    Normalize and tokenize text.

    Required behavior (tests rely on this):

      - Convert the string to lowercase.
      - Replace any NON-alphanumeric character (anything not [a-z0-9]) with a space.
      - Split on whitespace.
      - Filter out empty tokens.

    Examples:
      "Hello, World! 123" -> ["hello", "world", "123"]
      "RAG: Retrieval-Augmented   Generation!!!"
        -> ["rag", "retrieval", "augmented", "generation"]
    """
    chars = []
    for char in text.lower():
        if char.isalnum() or char == ' ':
            chars.append(char)
        else:
            chars.append(' ')
    text = "".join(chars)
    return text.split()



def build_index(documents: List[Document]) -> Dict[str, Dict[str, int]]:
    """
    Build an inverted index mapping term -> {doc_id: term_frequency}.

    Term frequency is defined as:
      - The total count of that term in the document's title + body.
      - Tokenization MUST use the tokenize() function above.

    Example (informal):

      docs = [
        Document(id="doc1", title="RAG intro", body="RAG connects LLMs", ...),
      ]

      index = build_index(docs)

      index["rag"] == {"doc1": 2}   # if "rag" appears twice in title+body
      index["llms"] == {"doc1": 1}

    Notes:
      - If a term appears multiple times, you must accumulate the count.
      - If a term only appears in some documents, only those doc_ids should
        show up in the inner dict.
    """
    index = defaultdict(dict)
    
    for doc in documents:
        text = doc.title + " " + doc.body
        tokens = tokenize(text)
        counts = Counter(tokens)
        for word, count in counts.items():
            if count > 0:
                index[word][doc.id] = count
    
    return index




def search(
    index: Dict[str, Dict[str, int]],
    documents: List[Document],
    query: str,
    max_results: int = 5,
    user_access_level: int | None = None,
) -> List[SearchResult]:
    """
    Search documents using simple term-frequency ranking with optional access control.

    Behavior (tests rely on this):

      1. Tokenize the query using tokenize().
      2. For each query token, look it up in the index and accumulate a score
         per document:
            score[doc_id] = sum(term_frequencies for all query terms)
      3. Ignore documents with score == 0.
      4. If user_access_level is NOT None, only consider documents where:
            doc.access_level <= user_access_level
         (i.e., user cannot see more restricted docs).
      5. Return a list of SearchResult(doc_id, score), sorted by:
            - score descending
            - then doc_id ascending (for deterministic ties)
      6. Truncate the list to at most max_results.

    Notes:
      - You will need a quick way to look up a document's access_level by id
        (e.g., build a dict from documents).
      - Score should be a float in the SearchResult, but you can accumulate it
        as an int and cast at the end.
    """
    query_tokens = tokenize(query)
    scores = defaultdict(int)
    id2doc = {doc.id: doc for doc in documents}
    for token in query_tokens:
        if token in index:
            for doc_id, score in index[token].items():
                if not id2doc[doc_id].access_level or not user_access_level:
                    scores[doc_id] += score
                elif id2doc[doc_id].access_level <= user_access_level:
                    scores[doc_id] += score
    results = []
    for doc_id, score in scores.items():
        results.append(SearchResult(doc_id=doc_id, score=score))
    results.sort(key=lambda x: (-x.score, x.doc_id))
    return results[:max_results]



def precision_at_k(gold_relevant: Set[str], retrieved: List[SearchResult], k: int) -> float:
    """
    Compute precision@k for a single query.

    Definitions:

      - gold_relevant: a set of doc_ids that are considered relevant.
      - retrieved: a ranked list of SearchResult objects.
      - k: cutoff rank.

    Required behavior (tests rely on this):

      - Consider ONLY the top-k retrieved results (or all of them if there are
        fewer than k results).
      - Let R be the set of doc_ids in those top-k positions.
      - precision@k = (number of doc_ids in R that are also in gold_relevant) / k

      - If k == 0, return 0.0.
      - If there are fewer than k retrieved docs, the denominator is STILL k,
        not len(retrieved).
      - If retrieved is empty and k > 0, return 0.0.

    Examples:
      gold_relevant = {"doc1", "doc3"}
      retrieved = [doc1, doc2, doc3]

      precision_at_k(gold_relevant, retrieved, k=1) -> 1/1  (doc1 is relevant)
      precision_at_k(gold_relevant, retrieved, k=2) -> 1/2  (only doc1 relevant)
      precision_at_k(gold_relevant, retrieved, k=3) -> 2/3  (doc1 and doc3 relevant)
    """
    if k <= 0:
        return 0.0
    count = 0
    for res in retrieved[:k]:
        if res.doc_id in gold_relevant:
            count += 1
    
    return count/k
