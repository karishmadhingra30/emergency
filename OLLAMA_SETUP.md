# Ollama Setup Guide for Emergency Chatbot

## Quick Start (Local Machine Setup)

This guide will help you install and configure Ollama on your local machine to use the Gemma 3 chatbot.

### Step 1: Install Ollama

#### For macOS:
```bash
# Using Homebrew
brew install ollama

# Or download from website
# Visit: https://ollama.com/download
```

#### For Linux:
```bash
# Download and install
curl -fsSL https://ollama.com/install.sh | sh
```

#### For Windows:
1. Download installer from: https://ollama.com/download
2. Run the installer
3. Ollama will start automatically

### Step 2: Start Ollama Service

#### macOS/Linux:
```bash
# Start Ollama in the background
ollama serve
```

Leave this terminal running, or set it up to run as a background service.

#### Windows:
Ollama should start automatically. Check system tray for Ollama icon.

### Step 3: Pull Gemma Model

Open a **new terminal** and run:

```bash
# For faster responses (recommended):
ollama pull gemma2:2b

# For better quality responses:
ollama pull gemma2:9b
```

This will download the model (may take a few minutes depending on your internet speed).

### Step 4: Verify Installation

```bash
# Check if model is installed
ollama list

# You should see something like:
# NAME            ID              SIZE    MODIFIED
# gemma2:2b       abc123def       1.6 GB  2 minutes ago
```

### Step 5: Test Ollama

```bash
# Quick test
ollama run gemma2:2b "Hello, how are you?"

# You should get a response from the model
```

### Step 6: Run the Application

Now that Ollama is running with the Gemma model, start the Flask app:

```bash
# In your emergency project directory
python app.py
```

You should see:
```
============================================================
Emergency Shelter Chatbot Backend
============================================================
Flask server: http://localhost:8080
Chatbot: Gemma 3 via Ollama
Shelters loaded: <number>
============================================================
```

### Step 7: Access the Chatbot

Open your browser and go to: **http://localhost:8080**

Try asking questions like:
- "What should I do for severe bleeding?"
- "Snake bite treatment"
- "Emergency numbers in India"

## Troubleshooting

### "Connection refused" or "Ollama not responding"

**Problem**: The chatbot shows an error about connecting to Ollama.

**Solution**:
```bash
# Make sure Ollama is running
ollama serve

# Check if Ollama is accessible
curl http://localhost:11434

# Should return: "Ollama is running"
```

### "Model not found"

**Problem**: Error says the model isn't available.

**Solution**:
```bash
# Pull the model
ollama pull gemma2:2b

# Verify it's installed
ollama list
```

### Ollama service won't start

**Problem**: `ollama serve` fails or won't start.

**Solution**:
```bash
# Check if another instance is running
ps aux | grep ollama

# Kill existing instances if needed
killall ollama

# Try starting again
ollama serve
```

### Port 11434 already in use

**Problem**: Ollama can't start because port is taken.

**Solution**:
```bash
# Find what's using the port
lsof -i :11434

# Kill the process or change Ollama port
export OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

Then update `gemma_chat.py` if you change the port.

### Slow responses

**Problem**: The chatbot takes a long time to respond.

**Solutions**:
1. Use the smaller model: `ollama pull gemma2:2b` (instead of 9b)
2. Ensure you have enough RAM (at least 4GB free for 2b model)
3. Close other memory-intensive applications
4. Consider upgrading hardware if consistently slow

### Fallback Mode (No Ollama)

If Ollama isn't available, the chatbot will automatically fall back to returning information from the first-aid knowledge base. You'll see emergency numbers and relevant first-aid information based on keywords in your question.

This fallback mode is useful for:
- Testing without Ollama
- Low-resource environments
- Emergency situations where AI isn't available

## Model Size Comparison

| Model      | Size  | RAM Required | Speed    | Quality |
|------------|-------|--------------|----------|---------|
| gemma2:2b  | 1.6GB | 4GB          | Fast     | Good    |
| gemma2:9b  | 5.5GB | 8GB          | Moderate | Better  |
| gemma2:27b | 16GB  | 16GB         | Slow     | Best    |

**Recommendation**: Use `gemma2:2b` for the emergency chatbot - it provides good quality responses with fast performance.

## System Requirements

### Minimum:
- 4GB RAM
- 2GB free disk space
- CPU with AVX support (most modern processors)
- Internet connection (for initial model download)

### Recommended:
- 8GB RAM
- 5GB free disk space
- Multi-core CPU
- SSD for faster model loading

## Running Ollama as a Service (Optional)

To have Ollama start automatically on system boot:

### Linux (systemd):
```bash
# Create systemd service
sudo tee /etc/systemd/system/ollama.service << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=$USER
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

# Enable and start service
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### macOS:
```bash
# Ollama typically runs automatically after installation
# To manually start:
brew services start ollama
```

## Need Help?

- **Ollama Documentation**: https://github.com/ollama/ollama
- **Gemma Model Info**: https://ollama.com/library/gemma2
- **Emergency App Issues**: Check the main README.md

---

**Note**: The emergency chatbot will work in fallback mode without Ollama, but AI-powered responses require Ollama to be running with the Gemma model installed.
