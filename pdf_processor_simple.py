"""
Simplified PDF Processing for First Aid Chatbot (No External Dependencies)

This version uses only Python built-in libraries for basic text extraction and search.
"""

import os
import re
import pickle
from typing import List, Dict, Tuple
from collections import Counter
import math

# Try to import PDF libraries
try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("⚠️  PyPDF2 not installed. Attempting basic text processing...")


class SimpleTextExtractor:
    """Fallback text extractor when PyPDF2 is not available"""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Fallback: Return empty string"""
        print(f"⚠️  Cannot extract text from {pdf_path} without PyPDF2")
        return ""


class SimpleTextChunker:
    """Simple text chunker that splits by sentences"""

    def __init__(self, chunk_size=1000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class SimpleTFIDFSearch:
    """Simple TF-IDF based search without numpy"""

    def __init__(self):
        self.documents = []
        self.vocabulary = set()
        self.idf = {}

    def build_index(self, documents: List[str]):
        """Build TF-IDF index"""
        self.documents = documents
        doc_count = len(documents)

        # Build vocabulary and document frequency
        doc_freq = Counter()
        for doc in documents:
            words = set(doc.lower().split())
            self.vocabulary.update(words)
            for word in words:
                doc_freq[word] += 1

        # Calculate IDF
        for word in self.vocabulary:
            self.idf[word] = math.log(doc_count / (1 + doc_freq[word]))

    def _compute_tf(self, text: str) -> Dict[str, float]:
        """Compute term frequency"""
        words = text.lower().split()
        word_count = Counter(words)
        total_words = len(words)

        tf = {}
        for word, count in word_count.items():
            tf[word] = count / total_words if total_words > 0 else 0

        return tf

    def _compute_tfidf_vector(self, text: str) -> Dict[str, float]:
        """Compute TF-IDF vector"""
        tf = self._compute_tf(text)
        tfidf = {}

        for word in self.vocabulary:
            tf_score = tf.get(word, 0)
            idf_score = self.idf.get(word, 0)
            tfidf[word] = tf_score * idf_score

        return tfidf

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity"""
        # Dot product
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in self.vocabulary)

        # Magnitudes
        mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def search(self, query: str, k: int = 3) -> List[Tuple[int, float]]:
        """Search for top-k most similar documents"""
        query_vector = self._compute_tfidf_vector(query)

        scores = []
        for idx, doc in enumerate(self.documents):
            doc_vector = self._compute_tfidf_vector(doc)
            similarity = self._cosine_similarity(query_vector, doc_vector)
            scores.append((idx, similarity))

        # Sort by similarity descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:k]


class PDFProcessor:
    """Process PDF documents and extract text"""

    def __init__(self, docs_folder="Docs"):
        self.docs_folder = docs_folder

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
        if not HAS_PYPDF2:
            return SimpleTextExtractor.extract_text_from_pdf(pdf_path)

        try:
            reader = PdfReader(pdf_path)
            text = ""
            total_pages = len(reader.pages)
            print(f"   Processing {total_pages} pages...")

            for i, page in enumerate(reader.pages):
                if i % 10 == 0:
                    print(f"   Progress: {i}/{total_pages} pages", end='\r')
                text += page.extract_text() + "\n\n"

            print(f"   Progress: {total_pages}/{total_pages} pages ✓")
            return text
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""

    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDFs in the Docs folder"""
        if not os.path.exists(self.docs_folder):
            print(f"❌ Docs folder not found: {self.docs_folder}")
            return []

        pdf_files = [f for f in os.listdir(self.docs_folder) if f.endswith('.pdf')]

        if not pdf_files:
            print(f"⚠️  No PDF files found in {self.docs_folder}")
            return []

        print(f"📚 Found {len(pdf_files)} PDF files\n")

        documents = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.docs_folder, pdf_file)
            print(f"📄 Processing: {pdf_file}")

            text = self.extract_text_from_pdf(pdf_path)
            if text:
                documents.append({
                    "text": text,
                    "source": pdf_file,
                    "path": pdf_path
                })
                print(f"   ✓ Extracted {len(text):,} characters\n")

        return documents


class SimpleVectorDatabase:
    """Simple vector database using TF-IDF"""

    def __init__(self):
        self.chunks = []
        self.metadata = []
        self.search_engine = SimpleTFIDFSearch()

    def add_documents(self, documents: List[Dict], chunk_size=1000, overlap=200):
        """Add documents to the database"""
        chunker = SimpleTextChunker(chunk_size=chunk_size, overlap=overlap)

        print(f"✂️  Chunking {len(documents)} documents...")

        for doc in documents:
            chunks = chunker.split_text(doc["text"])
            for i, chunk in enumerate(chunks):
                self.chunks.append(chunk)
                self.metadata.append({
                    "source": doc["source"],
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })

        print(f"📦 Created {len(self.chunks)} text chunks")

        # Build search index
        print("🔍 Building TF-IDF search index...")
        self.search_engine.build_index(self.chunks)
        print(f"✓ Index built with {len(self.search_engine.vocabulary):,} unique terms")

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for relevant chunks"""
        if not self.chunks:
            return []

        results_indices = self.search_engine.search(query, k=k)

        results = []
        for idx, score in results_indices:
            if idx < len(self.chunks):
                results.append({
                    "text": self.chunks[idx],
                    "metadata": self.metadata[idx],
                    "score": float(score)
                })

        return results

    def save(self, path="vectordb"):
        """Save database to disk"""
        os.makedirs(path, exist_ok=True)

        data = {
            "chunks": self.chunks,
            "metadata": self.metadata,
            "search_engine": self.search_engine
        }

        with open(os.path.join(path, "vectordb_simple.pkl"), "wb") as f:
            pickle.dump(data, f)

        print(f"💾 Vector database saved to {path}/")

    @classmethod
    def load(cls, path="vectordb"):
        """Load database from disk"""
        pkl_path = os.path.join(path, "vectordb_simple.pkl")

        if not os.path.exists(pkl_path):
            # Try loading old format
            pkl_path = os.path.join(path, "vectordb.pkl")
            if not os.path.exists(pkl_path):
                raise FileNotFoundError(f"Vector database not found in {path}")

        with open(pkl_path, "rb") as f:
            data = pickle.load(f)

        db = cls()
        db.chunks = data["chunks"]
        db.metadata = data["metadata"]
        db.search_engine = data["search_engine"]

        print(f"📖 Loaded vector database with {len(db.chunks)} chunks")
        return db


def build_vector_database():
    """Build vector database from PDFs"""
    print("\n" + "="*60)
    print("🏗️  Building Vector Database from PDF Documents")
    print("="*60 + "\n")

    # Process PDFs
    processor = PDFProcessor()
    documents = processor.process_all_pdfs()

    if not documents:
        print("\n❌ No documents processed. Please add PDF files to the Docs folder.")
        return None

    # Build vector database
    vectordb = SimpleVectorDatabase()
    vectordb.add_documents(documents)

    # Save to disk
    vectordb.save()

    print("\n" + "="*60)
    print("✅ Vector Database Built Successfully!")
    print("="*60)
    print(f"📊 Statistics:")
    print(f"   - Documents processed: {len(documents)}")
    print(f"   - Text chunks: {len(vectordb.chunks)}")
    print(f"   - Unique terms: {len(vectordb.search_engine.vocabulary):,}")
    print(f"   - Method: TF-IDF (no external dependencies)")
    print("\n💡 You can now use this database in gemma_chat.py for enhanced responses!\n")

    return vectordb


def test_retrieval():
    """Test the vector database retrieval"""
    print("\n" + "="*60)
    print("🧪 Testing Vector Database Retrieval")
    print("="*60 + "\n")

    # Load vector database
    if not os.path.exists("vectordb/vectordb_simple.pkl"):
        print("❌ Vector database not found. Run with --build first.")
        return

    vectordb = SimpleVectorDatabase.load()

    # Test queries
    test_queries = [
        "How do I treat a burn?",
        "What should I do for snake bite?",
        "CPR procedure steps",
        "How to stop bleeding?",
        "Symptoms of heart attack"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        results = vectordb.search(query, k=2)

        for i, result in enumerate(results, 1):
            print(f"\n[Result {i}] Score: {result['score']:.3f}")
            print(f"Source: {result['metadata']['source']}")
            print(f"Text: {result['text'][:200]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--build":
            build_vector_database()
        elif sys.argv[1] == "--test":
            test_retrieval()
        else:
            print("Usage:")
            print("  python pdf_processor_simple.py --build    # Build vector database")
            print("  python pdf_processor_simple.py --test     # Test retrieval")
    else:
        print("Usage:")
        print("  python pdf_processor_simple.py --build    # Build vector database")
        print("  python pdf_processor_simple.py --test     # Test retrieval")
