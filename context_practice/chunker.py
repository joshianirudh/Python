"""
Assignment 1: Document Chunker
===============================

Context: In RAG systems, documents need to be split into chunks for embedding and retrieval.
Your task is to implement a flexible document chunking system that supports multiple strategies.

Requirements:
1. Implement a DocumentChunker class that can chunk text using different strategies
2. Support fixed-size chunking with overlap
3. Support sentence-based chunking
4. Support paragraph-based chunking
5. Each chunk should include metadata (chunk_id, start_pos, end_pos, token_count estimate)
6. Handle edge cases (empty documents, single-word documents, etc.)

Time: 30-45 minutes
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ChunkStrategy(Enum):
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


@dataclass
class Chunk:
    """Represents a document chunk with metadata."""
    chunk_id: int
    text: str
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]


class DocumentChunker:
    """
    A flexible document chunking system for RAG pipelines.
    
    Your implementation should handle:
    - Different chunking strategies
    - Configurable chunk sizes and overlap
    - Proper boundary handling (don't split words)
    - Metadata generation for each chunk
    """
    
    def __init__(self, strategy: ChunkStrategy = ChunkStrategy.FIXED_SIZE, 
                 chunk_size: int = 500, overlap: int = 50):
        """
        Initialize the chunker.
        
        Args:
            strategy: The chunking strategy to use
            chunk_size: Target size for fixed-size chunks (in characters)
            overlap: Number of characters to overlap between chunks
        """
        # TODO: Implement initialization
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, document: str, doc_id: str = "default") -> List[Chunk]:
        """
        Chunk a document according to the configured strategy.
        
        Args:
            document: The text document to chunk
            doc_id: Identifier for the document (included in metadata)
            
        Returns:
            List of Chunk objects with text and metadata
        """
        # TODO: Implement chunking logic
        if self.strategy == ChunkStrategy['FIXED_SIZE']:
            return self._chunk_fixed_size(document, doc_id)
        elif self.strategy == ChunkStrategy['SENTENCE']:
            return self._chunk_by_sentences(document, doc_id)
        elif self.strategy == ChunkStrategy['PARAGRAPH']:
            return self._chunk_by_paragraphs(document, doc_id)
        else:
            return []

    
    def _chunk_fixed_size(self, document: str, doc_id: str) -> List[Chunk]:
        """
        Split document into fixed-size chunks with overlap.
        Should not split words - find nearest word boundary.
        """
        # TODO: Implement fixed-size chunking
        # metadata: (chunk_id, start_pos, end_pos, token_count, estimate)
        # chunk: id, text, start, end, metadata
        doc_len = len(document)
        sp, ep, id_ = 0, self.chunk_size, 0
        chunks = []
        while ep < doc_len:
            text = document[sp:ep]
            metadata = {
                        'doc_id': doc_id, 
                        'token_count': self._estimate_tokens(text), 
                        'strategy': self.strategy 
                        }
            chunk = Chunk(chunk_id=id_, text= text, start_pos=sp, end_pos=ep-1, metadata=metadata)
            chunks.append(chunk)
            sp = ep - self.overlap
            ep = sp + self.chunk_size
            id_ += 1
        if sp < doc_len:
            text= document[sp:]
            metadata = {
                        'doc_id': doc_id, 
                        'token_count': self._estimate_tokens(text), 
                        'strategy': self.strategy 
                        }
            chunks.append(Chunk(chunk_id=id_, text= text, start_pos=sp, end_pos=doc_len-1, metadata=metadata))
        return chunks
    
    def _chunk_by_sentences(self, document: str, doc_id: str) -> List[Chunk]:
        """
        Split document by sentences. Group sentences until reaching target size.
        Simple sentence detection: split on '. ', '! ', '? '
        """
        # TODO: Implement sentence-based chunking
        pass
    
    def _chunk_by_paragraphs(self, document: str, doc_id: str) -> List[Chunk]:
        """
        Split document by paragraphs (separated by double newlines).
        If a paragraph exceeds chunk_size, split it further.
        """
        # TODO: Implement paragraph-based chunking
        pass
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Rough token count estimation (1 token ≈ 4 characters).
        """
        return len(text) // 4


# ============================================================================
# TEST CASES - DO NOT MODIFY
# ============================================================================

def test_fixed_size_chunking():
    """Test fixed-size chunking with overlap."""
    document = "This is a test document. " * 50  # ~1250 chars
    chunker = DocumentChunker(strategy=ChunkStrategy.FIXED_SIZE, chunk_size=200, overlap=20)
    chunks = chunker.chunk_document(document, doc_id="test_doc")
    
    assert len(chunks) > 1, "Should create multiple chunks"
    assert all(isinstance(c, Chunk) for c in chunks), "Should return Chunk objects"
    assert chunks[0].chunk_id == 0, "First chunk should have ID 0"
    assert all(len(c.text) <= 220 for c in chunks), "Chunks should respect size limit (with buffer)"
    assert all(c.metadata.get("doc_id") == "test_doc" for c in chunks), "Should include doc_id in metadata"
    
    # Test overlap
    if len(chunks) > 1:
        overlap_text = document[chunks[1].start_pos:chunks[0].end_pos]
        assert len(overlap_text) > 0, "Should have overlap between chunks"
    
    print("✓ Fixed-size chunking test passed")


def test_empty_document():
    """Test handling of empty documents."""
    chunker = DocumentChunker()
    chunks = chunker.chunk_document("", doc_id="empty")
    
    assert len(chunks) == 0, "Empty document should return no chunks"
    print("✓ Empty document test passed")


def test_single_word():
    """Test handling of very short documents."""
    chunker = DocumentChunker(chunk_size=100)
    chunks = chunker.chunk_document("Hello", doc_id="short")
    
    assert len(chunks) == 1, "Single word should create one chunk"
    assert chunks[0].text == "Hello", "Should preserve the text"
    print("✓ Single word test passed")


def test_sentence_chunking():
    """Test sentence-based chunking."""
    document = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
    chunker = DocumentChunker(strategy=ChunkStrategy.SENTENCE, chunk_size=50)
    chunks = chunker.chunk_document(document, doc_id="sent_doc")
    
    assert len(chunks) > 1, "Should create multiple chunks"
    assert all(chunk.text.strip().endswith(('.', '!', '?')) or 
               chunk == chunks[-1] for chunk in chunks), "Chunks should end at sentence boundaries"
    print("✓ Sentence chunking test passed")


def test_paragraph_chunking():
    """Test paragraph-based chunking."""
    document = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."
    chunker = DocumentChunker(strategy=ChunkStrategy.PARAGRAPH, chunk_size=100)
    chunks = chunker.chunk_document(document, doc_id="para_doc")
    
    assert len(chunks) == 3, "Should create three chunks for three paragraphs"
    assert "First paragraph" in chunks[0].text, "Should preserve paragraph content"
    print("✓ Paragraph chunking test passed")


def test_chunk_metadata():
    """Test that chunks have proper metadata."""
    document = "Test document for metadata validation."
    chunker = DocumentChunker(chunk_size=20)
    chunks = chunker.chunk_document(document, doc_id="meta_doc")
    
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_id == i, f"Chunk {i} should have correct ID"
        assert chunk.start_pos >= 0, "Start position should be non-negative"
        assert chunk.end_pos > chunk.start_pos, "End position should be after start"
        assert "token_count" in chunk.metadata, "Should include token count estimate"
        assert chunk.metadata["token_count"] > 0, "Token count should be positive"
    
    print("✓ Chunk metadata test passed")


def test_no_word_splitting():
    """Test that words are not split in the middle."""
    document = "Supercalifragilisticexpialidocious is a very long word that should not be split."
    chunker = DocumentChunker(chunk_size=30)
    chunks = chunker.chunk_document(document)
    
    # Check that "Supercalifragilisticexpialidocious" is not split
    full_text = " ".join(c.text for c in chunks)
    assert "Supercalifragilisticexpialidocious" in full_text, "Long words should not be split"
    
    print("✓ No word splitting test passed")


def run_all_tests():
    """Run all test cases."""
    print("\nRunning Document Chunker Tests...")
    print("=" * 50)
    
    test_fixed_size_chunking()
    test_empty_document()
    test_single_word()
    test_sentence_chunking()
    test_paragraph_chunking()
    test_chunk_metadata()
    test_no_word_splitting()
    
    print("=" * 50)
    print("All tests passed! ✓\n")


if __name__ == "__main__":
    run_all_tests()