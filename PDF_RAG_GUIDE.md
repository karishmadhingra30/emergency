# PDF-Based RAG Enhancement Guide

## Overview

The chatbot now supports **Enhanced RAG (Retrieval-Augmented Generation)** using PDF documents. This allows the chatbot to retrieve relevant information from authoritative medical guidelines stored as PDFs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Query                               │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  gemma_chat.py          │
        │  (Enhanced Retrieval)   │
        └────┬───────────────┬────┘
             │               │
    ┌────────▼──────┐   ┌───▼──────────────┐
    │ PDF Vector DB │   │ Static Knowledge │
    │ (FAISS/Numpy) │   │ (first_aid_...) │
    └───────┬───────┘   └─────┬────────────┘
            │                 │
            └────────┬────────┘
                     │
        ┌────────────▼─────────────┐
        │  Combined Context        │
        │  (Top-k chunks)          │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │  Gemma 2B via Ollama     │
        │  (Generate Response)     │
        └──────────────────────────┘
```

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install PyPDF2 sentence-transformers faiss-cpu numpy
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Add PDF Documents

Place your first aid PDF documents in the `Docs/` folder:

```bash
Docs/
├── red_cross_first_aid_manual.pdf
├── who_emergency_care_guidelines.pdf
├── ndma_disaster_management.pdf
├── snake_bite_treatment_india.pdf
└── ... (add more PDFs)
```

**Recommended PDF Sources:**

- **Red Cross First Aid Manual** (American or Indian Red Cross)
- **WHO Emergency Care Guidelines**
- **St. John Ambulance First Aid Manual**
- **NDMA Disaster Management Handbooks** (India)
- **Indian Council of Medical Research (ICMR) Emergency Protocols**
- **Snake Bite Treatment Guidelines** (India-specific)

### Step 3: Build Vector Database

Run the PDF processor to extract text and create embeddings:

```bash
python pdf_processor.py --build
```

This will:
1. Extract text from all PDFs in the `Docs/` folder
2. Split text into ~1000 character chunks with 200 character overlap
3. Generate embeddings using sentence-transformers (or TF-IDF fallback)
4. Build a FAISS index (or numpy similarity search fallback)
5. Save the vector database to `vectordb/`

**Expected Output:**
```
📚 Found 5 PDF files
📄 Processing: red_cross_first_aid_manual.pdf
   ✓ Extracted 125,000 characters
...
✂️  Chunking 5 documents...
📦 Created 450 text chunks
🔮 Generating neural embeddings...
🚀 Building FAISS index...
✓ FAISS index built with 450 vectors
💾 Vector database saved to vectordb/
```

### Step 4: Test Retrieval

Test the vector database retrieval:

```bash
python pdf_processor.py --test
```

This will run test queries and show retrieved chunks with relevance scores.

### Step 5: Restart the Chatbot

The chatbot will automatically load the vector database on startup:

```bash
python app.py
```

You should see:
```
📚 Loading PDF vector database...
✓ Loaded vector database with 450 chunks
```

## How It Works

### 1. **Dual Retrieval System**

The enhanced chatbot uses **two retrieval sources**:

1. **PDF Vector Database** (Primary)
   - Semantic search using embeddings
   - Retrieves most relevant passages from PDF guidelines
   - Higher priority in context construction

2. **Static Knowledge Base** (Fallback)
   - Keyword-based retrieval from `first_aid_knowledge.py`
   - 18 pre-defined topics with structured data
   - Always available, even without PDFs

### 2. **Retrieval Flow**

```python
User Query: "How do I treat a severe burn?"
    ↓
PDF Search: Finds 3 most relevant chunks from medical PDFs
    → Chunk 1: "Burns: Second-Degree Treatment..." (Score: 0.87)
    → Chunk 2: "Burn Management Protocol..." (Score: 0.82)
    → Chunk 3: "Emergency Burn Care Steps..." (Score: 0.78)
    ↓
Static Search: Finds matching topics from static knowledge
    → Topic: "burns" → Steps, warnings, symptoms
    ↓
Combined Context:
    [PDF Chunk 1]
    [PDF Chunk 2]
    [PDF Chunk 3]
    [Static Knowledge: burns]
    ↓
Gemma 2B: Generates response using combined context
```

### 3. **Embedding Models**

The system supports multiple embedding backends:

| Backend | Model | Dimension | Speed | Quality |
|---------|-------|-----------|-------|---------|
| **sentence-transformers** (Preferred) | `all-MiniLM-L6-v2` | 384 | Fast | High |
| **TF-IDF** (Fallback) | Custom | Variable | Very Fast | Medium |

### 4. **Index Types**

| Index | Library | Speed | Memory |
|-------|---------|-------|--------|
| **FAISS** (Preferred) | Facebook AI | Very Fast | Low |
| **Numpy** (Fallback) | NumPy | Fast | Low |

## Configuration

### Chunk Size and Overlap

Edit `pdf_processor.py` to adjust chunking:

```python
# Default values
chunk_size = 1000   # ~200 words per chunk
overlap = 200       # Preserve context between chunks
```

### Number of Retrieved Chunks

Edit `gemma_chat.py` to change retrieval count:

```python
# In retrieve_relevant_knowledge method
pdf_results = self.vector_db.search(user_message, k=3)  # Change k value
```

### Relevance Threshold

Add a relevance threshold to filter low-quality matches:

```python
# In gemma_chat.py, retrieve_relevant_knowledge method
pdf_results = self.vector_db.search(user_message, k=top_k)
for result in pdf_results:
    if result['score'] > 0.5:  # Only use chunks with >50% relevance
        pdf_chunks.append(...)
```

## Performance

### Without PDF RAG (Baseline)
- **Knowledge Source:** Static 18 topics (~651 lines)
- **Retrieval Method:** Keyword matching
- **Latency:** ~1-2 seconds
- **Coverage:** Limited to pre-defined topics

### With PDF RAG (Enhanced)
- **Knowledge Source:** Unlimited PDFs + Static knowledge
- **Retrieval Method:** Semantic search + keyword matching
- **Latency:** ~2-3 seconds (embedding + generation)
- **Coverage:** Comprehensive medical guidelines

### Optimization Tips

1. **Use GPU for embeddings** (if available):
   ```python
   # In pdf_processor.py
   model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
   ```

2. **Reduce chunk count** for faster retrieval:
   ```python
   # Retrieve fewer chunks
   k=2 instead of k=3
   ```

3. **Pre-filter by keywords** before vector search:
   ```python
   # Add keyword pre-filtering in gemma_chat.py
   if "burn" in message_lower:
       search_in_burn_pdfs_only()
   ```

## Troubleshooting

### Issue: "PyPDF2 not installed"

**Solution:**
```bash
pip install PyPDF2
```

The system will work with fallback text extraction if PyPDF2 is not available.

### Issue: "sentence-transformers not installed"

**Solution:**
```bash
pip install sentence-transformers
```

The system will automatically fall back to TF-IDF embeddings.

### Issue: "faiss not installed"

**Solution:**
```bash
pip install faiss-cpu
```

The system will use numpy-based similarity search as fallback.

### Issue: No PDFs found

**Solution:**
- Ensure PDFs are in the `Docs/` folder
- PDFs must have `.pdf` extension
- Check file permissions

### Issue: Low retrieval quality

**Solutions:**
1. Add more relevant PDF documents
2. Increase chunk overlap for better context
3. Use better embedding model (e.g., `all-mpnet-base-v2`)
4. Filter PDFs to first-aid specific content only

## Updating the Database

When you add new PDFs or modify existing ones:

```bash
# Rebuild the vector database
python pdf_processor.py --build

# Restart the chatbot
python app.py
```

The chatbot will automatically load the updated database.

## Advanced: Custom Embeddings

To use a different embedding model:

```python
# In pdf_processor.py, VectorDatabase.__init__
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # Better quality, slower
# or
self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # Multilingual
```

## File Structure

```
emergency/
├── Docs/                          # PDF documents folder
│   ├── README.md
│   └── *.pdf                      # Your PDF files
├── vectordb/                      # Generated vector database
│   ├── vectordb.pkl              # Chunks, metadata, embeddings
│   ├── faiss.index               # FAISS index (if available)
│   └── tfidf.pkl                 # TF-IDF model (fallback)
├── pdf_processor.py              # PDF processing script
├── gemma_chat.py                 # Enhanced chatbot with RAG
└── PDF_RAG_GUIDE.md              # This file
```

## API Integration

The enhanced chatbot is fully compatible with the existing API:

```python
# In your app
from gemma_chat import gemma_chat

response = gemma_chat("How to treat a burn?")
# Response will automatically include PDF knowledge if available
```

No code changes needed - the enhancement is transparent!

## Benefits

✅ **Authoritative Sources**: Use official medical guidelines (Red Cross, WHO, etc.)

✅ **Comprehensive Coverage**: Not limited to 18 pre-defined topics

✅ **Semantic Search**: Finds relevant passages even with different wording

✅ **India-Specific**: Add NDMA, ICMR, and local guidelines

✅ **Transparent Fallback**: Works with or without PDFs

✅ **Easy Updates**: Just add PDFs and rebuild database

## Next Steps

1. **Collect PDFs**: Gather authoritative first aid and disaster management PDFs
2. **Build Database**: Run `python pdf_processor.py --build`
3. **Test Queries**: Run `python pdf_processor.py --test`
4. **Deploy**: Restart the chatbot to use enhanced RAG
5. **Monitor**: Check response quality and add more PDFs as needed

## Resources

- **sentence-transformers**: https://www.sbert.net/
- **FAISS**: https://github.com/facebookresearch/faiss
- **PyPDF2**: https://pypdf2.readthedocs.io/
- **Red Cross First Aid**: https://www.redcross.org/take-a-class/first-aid
- **WHO Emergency Care**: https://www.who.int/emergencies
- **NDMA Guidelines**: https://ndma.gov.in

---

**Created**: 2025-12-09
**Version**: 1.0
**Compatibility**: Gemma 2B via Ollama, Python 3.8+
