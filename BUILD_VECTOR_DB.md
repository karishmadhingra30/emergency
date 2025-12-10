# Building the Vector Database - Quick Start Guide

## Current Status

✅ **10 PDF documents successfully added** (118 MB total):
- IFRCFirstAidManual.pdf (4.3 MB)
- IndianFirstAidManual.pdf (11 MB)
- RedCossWildernessFirstAidManual.pdf (14 MB)
- SAS Survival Handbook2009.pdf (34 MB)
- Standard-Treatment-Guidelines-for-Management-of-Snake-Bite.pdf (5.1 MB)
- USArmyFull-First-Aid-Manual-FM-2111.pdf (2.4 MB)
- USArmySurvival.pdf (21 MB)
- WHOSnakebiteManagement.pdf (25 MB)
- Wilderness Remote FirstAid_PocketGuide.pdf (1.3 MB)
- snake_bit_India.pdf (551 KB)

✅ **PDF processing scripts created**:
- `pdf_processor.py` - Full version with sentence-transformers & FAISS
- `pdf_processor_simple.py` - Simplified version with TF-IDF only

⚠️ **Dependencies required** (install before building):
```bash
pip install PyPDF2 sentence-transformers faiss-cpu numpy
```

## Option 1: Full Build (Recommended - Best Quality)

**Requires**: PyPDF2, sentence-transformers, faiss-cpu, numpy

```bash
# Install dependencies
pip install PyPDF2 sentence-transformers faiss-cpu numpy

# Build vector database
python3 pdf_processor.py --build

# Test retrieval
python3 pdf_processor.py --test
```

**Benefits**:
- Neural embeddings (sentence-transformers)
- Fast FAISS search
- High-quality semantic search

## Option 2: Simple Build (Works Without ML Libraries)

**Requires**: Only PyPDF2

```bash
# Install minimal dependency
pip install PyPDF2

# Build with TF-IDF search
python3 pdf_processor_simple.py --build

# Test retrieval
python3 pdf_processor_simple.py --test
```

**Benefits**:
- No ML dependencies needed
- Works on any Python installation
- Still provides good search quality

## Option 3: Quick Setup Script

Use the automated setup script:

```bash
./setup_pdf_rag.sh
```

This will:
1. Check for PDFs in Docs/
2. Install dependencies (if possible)
3. Build vector database automatically
4. Provide status updates

## After Building

Once the vector database is built, restart the chatbot:

```bash
python app.py
```

The chatbot will automatically load the PDF knowledge on startup:

```
📚 Loading PDF vector database...
✓ Loaded vector database with [X] chunks
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyPDF2'"

**Solution**:
```bash
pip install PyPDF2
```

Or use system package manager:
```bash
apt-get install python3-pypdf2  # Ubuntu/Debian
```

### "No module named 'numpy'"

**Option A**: Install numpy
```bash
pip install numpy
```

**Option B**: Use simplified version
```bash
python3 pdf_processor_simple.py --build
```

### Network/Proxy Issues

If pip install fails due to network issues:

1. **Download packages offline** and install locally:
   ```bash
   # On a machine with internet:
   pip download PyPDF2 sentence-transformers faiss-cpu numpy

   # Transfer files to target machine, then:
   pip install --no-index --find-links . PyPDF2 sentence-transformers faiss-cpu numpy
   ```

2. **Use system package manager** (if available):
   ```bash
   apt-get install python3-pypdf2 python3-numpy
   ```

3. **Use Docker** with pre-installed dependencies

## Expected Output

When building successfully:

```
============================================================
🏗️  Building Vector Database from PDF Documents
============================================================

📚 Found 10 PDF files

📄 Processing: IFRCFirstAidManual.pdf
   Processing 100 pages...
   ✓ Extracted 250,000 characters

[... more files ...]

✂️  Chunking 10 documents...
📦 Created 1,234 text chunks
🔮 Generating neural embeddings...
🚀 Building FAISS index...
✓ FAISS index built with 1,234 vectors
💾 Vector database saved to vectordb/

============================================================
✅ Vector Database Built Successfully!
============================================================
📊 Statistics:
   - Documents processed: 10
   - Text chunks: 1,234
   - Embedding method: Neural (sentence-transformers)
   - Index type: FAISS

💡 You can now use this database in gemma_chat.py for enhanced responses!
```

## Integration Status

✅ **gemma_chat.py** already integrated - will auto-load vector database
✅ **Fallback system** - works with or without PDF knowledge
✅ **No API changes** - transparent enhancement

## File Structure After Build

```
emergency/
├── Docs/                          # Your PDF documents (118 MB)
│   ├── IFRCFirstAidManual.pdf
│   ├── IndianFirstAidManual.pdf
│   └── ... (8 more PDFs)
│
├── vectordb/                      # Generated database
│   ├── vectordb.pkl              # or vectordb_simple.pkl
│   ├── faiss.index               # (if using full version)
│   └── tfidf.pkl                 # (if using simple version)
│
├── pdf_processor.py              # Full processor
├── pdf_processor_simple.py       # Simple processor
├── setup_pdf_rag.sh              # Automated setup
└── gemma_chat.py                 # Enhanced chatbot (already integrated)
```

## Next Steps

1. **Install dependencies** (PyPDF2 minimum, full ML stack recommended)
2. **Run build script**: `python3 pdf_processor.py --build`
3. **Test retrieval**: `python3 pdf_processor.py --test`
4. **Start chatbot**: `python app.py`
5. **Test queries** like "How to treat snake bite?" and see PDF knowledge in responses

## Performance Comparison

| Method | Setup Time | Search Quality | Dependencies |
|--------|------------|----------------|--------------|
| Full (FAISS + Transformers) | 5-10 min | Excellent | PyPDF2, transformers, faiss, numpy |
| Simple (TF-IDF) | 2-5 min | Good | PyPDF2 only |
| None (Static knowledge) | 0 min | Basic | None |

## Support

- Full documentation: `PDF_RAG_GUIDE.md`
- Training strategy: `TRAINING_STRATEGY.md`
- Architecture docs: `ARCHITECTURE.md`

---

**Note**: The current environment has network restrictions preventing package installation. The scripts and PDFs are ready - you just need to run the build command in an environment where dependencies can be installed (local machine, Docker, etc.).
