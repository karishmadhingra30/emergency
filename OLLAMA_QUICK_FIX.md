# Ollama Setup Guide - Quick Fix

## Issue: "Failed to connect to Ollama" Error

If you're seeing this error, Ollama either isn't installed or isn't running.

---

## Quick Setup (3 Steps)

### Step 1: Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
# Download from https://ollama.com/download
# Or use Homebrew:
brew install ollama
```

**Windows:**
Download installer from https://ollama.com/download

### Step 2: Start Ollama Service

**Linux/macOS:**
```bash
# Start Ollama in the background
ollama serve &

# Or in a separate terminal:
ollama serve
```

**Windows:**
Ollama starts automatically as a service after installation

### Step 3: Download Gemma Model

```bash
ollama pull gemma2:2b
```

This downloads the Gemma 2B model (~1.6 GB)

---

## Verify Setup

Test if Ollama is working:

```bash
# Check if Ollama is running
curl http://localhost:11434

# Should return: "Ollama is running"

# Test the model
ollama run gemma2:2b "Hello"
```

If you get a response, Ollama is working correctly!

---

## Start Your Chatbot

Once Ollama is running:

```bash
python app.py
```

Expected output:
```
⚠️  PDF vector database not available. Using static knowledge only.
 * Running on http://127.0.0.1:8080
```

(The PDF warning is normal until you build the vector database)

---

## Troubleshooting

### "Ollama serve: command not found"
- Ollama not installed correctly
- Solution: Reinstall using Step 1

### "Connection refused on port 11434"
- Ollama service not running
- Solution: Run `ollama serve` in a terminal

### "Model not found: gemma2:2b"
- Model not downloaded
- Solution: Run `ollama pull gemma2:2b`

### Still getting errors?
The chatbot has a fallback mode:
- It will still provide first aid guidance from the static knowledge base
- Emergency numbers will always be shown
- The system degrades gracefully without Ollama

---

## Alternative: Run Without Ollama (Fallback Mode)

The chatbot will work in fallback mode using only the static knowledge base:

**Pros:**
- No Ollama installation needed
- Faster responses
- Works offline

**Cons:**
- Simpler responses (no AI generation)
- Fixed knowledge base only
- No PDF RAG enhancement

To use fallback mode, just start the app without Ollama running:
```bash
python app.py
```

The chatbot will automatically use static knowledge.

---

## Optional: Build PDF Vector Database

Once Ollama is working, you can enable PDF RAG:

```bash
# Install PDF dependencies
pip install PyPDF2 sentence-transformers faiss-cpu numpy

# Build vector database
python pdf_processor.py --build

# Restart app
python app.py
```

Expected startup with PDF RAG:
```
📚 Loading PDF vector database...
✓ Loaded vector database with 1,234 chunks
 * Running on http://127.0.0.1:8080
```

---

## Quick Reference

**Start Ollama:**
```bash
ollama serve
```

**Download Model:**
```bash
ollama pull gemma2:2b
```

**Start Chatbot:**
```bash
python app.py
```

**Check Ollama Status:**
```bash
curl http://localhost:11434
```

---

That's it! Your chatbot should now work properly. 🎉
