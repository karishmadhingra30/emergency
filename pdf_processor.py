"""
PDF Processing and Vector Database Builder for First Aid Chatbot

This script processes PDF documents from the Docs folder and creates a vector database
for enhanced RAG (Retrieval-Augmented Generation) retrieval.

Usage:
    python pdf_processor.py --build    # Build vector database from PDFs
    python pdf_processor.py --test     # Test the retrieval system
"""

import os
import re
import json
import pickle
from typing import List, Dict, Tuple
import numpy as np

# Try to import PDF libraries, fallback to basic implementation
try:
    from PyPDF2 import PdfReader
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("⚠️  PyPDF2 not installed. Will use fallback text extraction.")

# Try to import advanced NLP libraries
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("⚠️  sentence-transformers not installed. Using TF-IDF fallback.")

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("⚠️  faiss not installed. Using numpy similarity search.")


class SimpleTextChunker:
    """Simple text chunker that splits by sentences and groups them into chunks"""

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


class SimpleTFIDFVectorizer:
    """Simple TF-IDF vectorizer for text embedding fallback"""

    def __init__(self):
        self.vocabulary = {}
        self.idf_scores = {}
        self.documents = []

    def fit(self, documents: List[str]):
        """Build vocabulary and compute IDF scores"""
        self.documents = documents
        word_doc_count = {}

        # Build vocabulary
        for doc in documents:
            words = set(doc.lower().split())
            for word in words:
                if word not in self.vocabulary:
                    self.vocabulary[word] = len(self.vocabulary)
                word_doc_count[word] = word_doc_count.get(word, 0) + 1

        # Compute IDF scores
        num_docs = len(documents)
        for word, doc_count in word_doc_count.items():
            self.idf_scores[word] = np.log(num_docs / (1 + doc_count))

    def transform(self, text: str) -> np.ndarray:
        """Convert text to TF-IDF vector"""
        vector = np.zeros(len(self.vocabulary))
        words = text.lower().split()
        word_count = {}

        # Count word frequencies
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        # Compute TF-IDF
        for word, count in word_count.items():
            if word in self.vocabulary:
                tf = count / len(words)
                idf = self.idf_scores.get(word, 0)
                vector[self.vocabulary[word]] = tf * idf

        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector


class PDFProcessor:
    """Process PDF documents and extract text"""

    def __init__(self, docs_folder="Docs"):
        self.docs_folder = docs_folder

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
        if not HAS_PYPDF2:
            print(f"⚠️  Cannot extract text from {pdf_path} - PyPDF2 not installed")
            return ""

        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"

            # Clean the extracted text
            text = self._clean_extracted_text(text)

            return text
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""

    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted PDF text by removing artifacts"""
        # Remove page numbers (standalone numbers)
        text = re.sub(r'\n\d{1,4}\n', '\n', text)

        # Remove common headers/footers patterns
        text = re.sub(r'\n[A-Z\s]{3,30}\n', '\n', text)  # ALL CAPS headers

        # Remove document reference codes (e.g., "3-2FM 4-25.11/NTRP 4-02.1/AFMAN 44-163(I)")
        text = re.sub(r'\d+-\d+[A-Z]{2,}\s+[\d\-\.\/A-Z\(\)]+', '', text)

        # Remove standalone reference numbers
        text = re.sub(r'\b\d{1,2}-\d{1,2}\b', '', text)

        # Remove multiple consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove extra whitespace
        text = re.sub(r' {2,}', ' ', text)

        # Fix broken words (remove single-character lines that aren't bullets)
        lines = text.split('\n')
        cleaned_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            # Keep bullet points and meaningful single-character lines
            if len(line) == 1 and line not in ['•', '◦', '-', '*', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                # This is likely a page number or artifact, skip it
                continue
            cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)

        return text.strip()

    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDFs in the Docs folder"""
        if not os.path.exists(self.docs_folder):
            print(f"❌ Docs folder not found: {self.docs_folder}")
            return []

        pdf_files = [f for f in os.listdir(self.docs_folder) if f.endswith('.pdf')]

        if not pdf_files:
            print(f"⚠️  No PDF files found in {self.docs_folder}")
            return []

        print(f"📚 Found {len(pdf_files)} PDF files")

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
                print(f"   ✓ Extracted {len(text)} characters")

        return documents


class VectorDatabase:
    """Vector database for semantic search"""

    def __init__(self, embedding_model=None):
        self.chunks = []
        self.metadata = []
        self.embeddings = None
        self.embedding_model = embedding_model
        self.use_neural = HAS_SENTENCE_TRANSFORMERS
        self.use_faiss = HAS_FAISS

        if self.use_neural and embedding_model is None:
            print("🧠 Loading sentence-transformers model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        elif not self.use_neural:
            print("📊 Using TF-IDF fallback for embeddings")
            self.tfidf = SimpleTFIDFVectorizer()

    def add_documents(self, documents: List[Dict], chunk_size=1000, overlap=200):
        """Add documents to the vector database"""
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

        # Create embeddings
        if self.use_neural:
            print("🔮 Generating neural embeddings...")
            self.embeddings = self.embedding_model.encode(
                self.chunks,
                show_progress_bar=True,
                convert_to_numpy=True
            )
        else:
            print("🔢 Generating TF-IDF embeddings...")
            self.tfidf.fit(self.chunks)
            self.embeddings = np.array([
                self.tfidf.transform(chunk) for chunk in self.chunks
            ])

        # Build FAISS index if available
        if self.use_faiss and self.embeddings is not None:
            print("🚀 Building FAISS index...")
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings.astype('float32'))
            print(f"✓ FAISS index built with {self.index.ntotal} vectors")

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for relevant chunks"""
        if not self.chunks:
            return []

        # Generate query embedding
        if self.use_neural:
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)[0]
        else:
            query_embedding = self.tfidf.transform(query)

        # Search
        if self.use_faiss:
            # Use FAISS for fast similarity search
            distances, indices = self.index.search(
                query_embedding.reshape(1, -1).astype('float32'), k
            )
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx < len(self.chunks):
                    results.append({
                        "text": self.chunks[idx],
                        "metadata": self.metadata[idx],
                        "score": float(1 / (1 + dist))  # Convert distance to similarity
                    })
        else:
            # Use numpy for similarity search
            similarities = np.dot(self.embeddings, query_embedding)
            top_indices = np.argsort(similarities)[-k:][::-1]

            results = []
            for idx in top_indices:
                results.append({
                    "text": self.chunks[idx],
                    "metadata": self.metadata[idx],
                    "score": float(similarities[idx])
                })

        return results

    def save(self, path="vectordb"):
        """Save vector database to disk"""
        os.makedirs(path, exist_ok=True)

        data = {
            "chunks": self.chunks,
            "metadata": self.metadata,
            "embeddings": self.embeddings,
            "use_neural": self.use_neural,
            "use_faiss": self.use_faiss
        }

        with open(os.path.join(path, "vectordb.pkl"), "wb") as f:
            pickle.dump(data, f)

        if self.use_faiss and hasattr(self, 'index'):
            faiss.write_index(self.index, os.path.join(path, "faiss.index"))

        # Save TF-IDF model if used
        if not self.use_neural:
            with open(os.path.join(path, "tfidf.pkl"), "wb") as f:
                pickle.dump(self.tfidf, f)

        print(f"💾 Vector database saved to {path}/")

    @classmethod
    def load(cls, path="vectordb"):
        """Load vector database from disk"""
        with open(os.path.join(path, "vectordb.pkl"), "rb") as f:
            data = pickle.load(f)

        db = cls()
        db.chunks = data["chunks"]
        db.metadata = data["metadata"]
        db.embeddings = data["embeddings"]
        db.use_neural = data["use_neural"]
        db.use_faiss = data["use_faiss"]

        # Load embedding model
        if db.use_neural:
            db.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            with open(os.path.join(path, "tfidf.pkl"), "rb") as f:
                db.tfidf = pickle.load(f)

        # Load FAISS index
        if db.use_faiss and os.path.exists(os.path.join(path, "faiss.index")):
            db.index = faiss.read_index(os.path.join(path, "faiss.index"))

        print(f"📖 Loaded vector database with {len(db.chunks)} chunks")
        return db


def build_vector_database():
    """Build vector database from PDFs in Docs folder"""
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
    vectordb = VectorDatabase()
    vectordb.add_documents(documents)

    # Save to disk
    vectordb.save()

    print("\n" + "="*60)
    print("✅ Vector Database Built Successfully!")
    print("="*60)
    print(f"📊 Statistics:")
    print(f"   - Documents processed: {len(documents)}")
    print(f"   - Text chunks: {len(vectordb.chunks)}")
    print(f"   - Embedding method: {'Neural (sentence-transformers)' if vectordb.use_neural else 'TF-IDF'}")
    print(f"   - Index type: {'FAISS' if vectordb.use_faiss else 'Numpy'}")
    print("\n💡 You can now use this database in gemma_chat.py for enhanced responses!\n")

    return vectordb


def test_retrieval():
    """Test the vector database retrieval"""
    print("\n" + "="*60)
    print("🧪 Testing Vector Database Retrieval")
    print("="*60 + "\n")

    # Load vector database
    if not os.path.exists("vectordb/vectordb.pkl"):
        print("❌ Vector database not found. Run with --build first.")
        return

    vectordb = VectorDatabase.load()

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
            print("  python pdf_processor.py --build    # Build vector database")
            print("  python pdf_processor.py --test     # Test retrieval")
    else:
        print("Usage:")
        print("  python pdf_processor.py --build    # Build vector database")
        print("  python pdf_processor.py --test     # Test retrieval")
