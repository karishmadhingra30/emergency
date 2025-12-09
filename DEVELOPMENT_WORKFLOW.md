# Development & Testing Workflow

## Understanding What's Running

When you're developing with the Gemma chatbot, you'll typically have **2-3 terminal windows** open:

### Terminal 1: Ollama Service
```bash
ollama serve
```
- **What it does**: Runs the Ollama backend that hosts the Gemma model
- **Keep it running**: YES - Leave this running all the time
- **Restart needed when**: Only if Ollama crashes or you reboot your computer
- **Output**: Shows model loading and inference requests

### Terminal 2: Flask Application
```bash
python app.py
```
- **What it does**: Runs your Flask web server that handles the chatbot and shelter APIs
- **Keep it running**: While testing, but restart after code changes
- **Restart needed when**: Every time you change Python code (app.py, gemma_chat.py, etc.)
- **Output**: Shows HTTP requests, errors, and chatbot activity

### Terminal 3: Git/Development Commands
- **What it does**: Used for git pull, testing, debugging
- **Keep it running**: Use as needed for commands
- **Output**: Your command outputs

---

## Complete Testing Workflow

### Step 1: Check Current Status

First, understand what's running:

```bash
# Check if Ollama is running
curl http://localhost:11434
# Should return: "Ollama is running"

# Check if Flask app is running
curl http://localhost:8080/health
# Should return JSON with chatbot status

# Check your git status
git status
git log -1
# See what branch you're on and latest commit
```

### Step 2: Pull Latest Changes from GitHub

**You do NOT need to close Ollama**, but you should stop the Flask app first.

**In Terminal 2 (Flask app):**
```bash
# Stop the Flask app
# Press: Ctrl+C
```

**In Terminal 3 (or Terminal 2 after stopping Flask):**
```bash
# Make sure you're in the right directory
cd /path/to/emergency

# Check what branch you're on
git branch

# Fetch latest changes
git fetch origin

# Pull the latest code from the feature branch
git pull origin claude/integrate-gemma-ollama-015dL8U9mohh6cVcaLKWJ7iG

# Or if you're on main and want to merge the feature:
# git pull origin main
```

### Step 3: Review What Changed

```bash
# See what files changed
git log -3 --oneline
git diff HEAD~1

# Check if requirements.txt was updated
git diff HEAD~1 requirements.txt
```

### Step 4: Update Dependencies (If Needed)

Only if `requirements.txt` changed:

```bash
# Install new dependencies
pip install -r requirements.txt

# Or update specific package
pip install --upgrade ollama
```

### Step 5: Restart Flask Application

**Leave Terminal 1 (Ollama) running!**

**In Terminal 2:**
```bash
# Start Flask app with your new code
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

### Step 6: Test Your Changes

**In your web browser:**
```
http://localhost:8080
```

Test the chatbot with queries like:
- "What should I do for bleeding?"
- "Snake bite treatment"
- "Find nearest shelter"

**Or test via command line (Terminal 3):**
```bash
# Test health endpoint
curl http://localhost:8080/health

# Test chat endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What to do for snake bite?", "sender": "test"}'
```

---

## Quick Reference: When to Restart What

| You changed...          | Restart Ollama? | Restart Flask? | git pull needed? |
|-------------------------|-----------------|----------------|------------------|
| Python code (app.py)    | ❌ NO           | ✅ YES         | If from GitHub   |
| gemma_chat.py          | ❌ NO           | ✅ YES         | If from GitHub   |
| first_aid_knowledge.py | ❌ NO           | ✅ YES         | If from GitHub   |
| HTML/CSS files         | ❌ NO           | ⚠️ Maybe*      | If from GitHub   |
| requirements.txt       | ❌ NO           | ✅ YES         | YES              |
| Changed Gemma model    | ✅ YES          | ✅ YES         | ❌ NO            |
| README.md only         | ❌ NO           | ❌ NO          | If you want to   |

*Flask serves static files; might need restart depending on caching

---

## Common Scenarios

### Scenario 1: Code updated on GitHub, test locally

```bash
# Terminal 2: Stop Flask (Ctrl+C)

# Terminal 3: Pull changes
git pull origin claude/integrate-gemma-ollama-015dL8U9mohh6cVcaLKWJ7iG
pip install -r requirements.txt  # Only if requirements changed

# Terminal 2: Restart Flask
python app.py

# Browser: Test at http://localhost:8080
```

**Do NOT restart Ollama** - it can keep running!

### Scenario 2: Made local changes, want to test

```bash
# Terminal 2: Stop Flask (Ctrl+C)

# Terminal 2: Restart Flask with your changes
python app.py

# Browser: Test at http://localhost:8080
```

### Scenario 3: Changed the Gemma model

```bash
# Terminal 1: Stop Ollama (Ctrl+C)

# Terminal 3: Pull new model
ollama pull gemma2:9b

# Update gemma_chat.py if needed to use new model

# Terminal 1: Restart Ollama
ollama serve

# Terminal 2: Restart Flask (Ctrl+C, then python app.py)

# Browser: Test at http://localhost:8080
```

### Scenario 4: Everything is broken, start fresh

```bash
# Terminal 1 & 2: Stop everything (Ctrl+C in both)

# Terminal 3: Clean restart
killall ollama  # Make sure no Ollama processes
git status      # Check for conflicts
git pull origin claude/integrate-gemma-ollama-015dL8U9mohh6cVcaLKWJ7iG

# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Flask
python app.py

# Browser: Test at http://localhost:8080
```

---

## Debugging Tips

### Check if Ollama is actually running

```bash
# Method 1: curl test
curl http://localhost:11434

# Method 2: Process check
ps aux | grep ollama

# Method 3: Test with model
ollama list
ollama run gemma2:2b "test"
```

### Check if Flask is running

```bash
# Method 1: curl test
curl http://localhost:8080/health

# Method 2: Process check
ps aux | grep "python.*app.py"

# Method 3: Check port
lsof -i :8080
```

### View Flask logs in real-time

Flask will show all requests in Terminal 2. Watch for:
- `POST /chat` - Chatbot requests
- `GET /health` - Health checks
- Errors in red

### Test without browser

```bash
# Quick chat test
python -c "
from gemma_chat import gemma_chat
result = gemma_chat('bleeding treatment')
print(result[0]['text'][:200])
"
```

---

## Git Workflow Best Practices

### Before pulling changes

```bash
# Save your work first
git status
git stash  # If you have uncommitted changes
git pull origin claude/integrate-gemma-ollama-015dL8U9mohh6cVcaLKWJ7iG
git stash pop  # Restore your changes if stashed
```

### If you get merge conflicts

```bash
git status  # See conflicting files
# Edit files to resolve conflicts
git add <resolved-files>
git commit -m "Resolve merge conflicts"
```

### Working on a new feature

```bash
# Create a new branch from the current feature branch
git checkout -b my-new-feature
# Make changes
git add .
git commit -m "Add my feature"
git push origin my-new-feature
```

---

## Performance Monitoring

### Check Ollama memory usage

```bash
# See how much memory Ollama is using
ps aux | grep ollama | awk '{print $6/1024 " MB"}'

# Or more detailed:
top -p $(pgrep ollama)
```

### Check Flask response times

Watch Terminal 2 for request times:
```
127.0.0.1 - - [08/Dec/2025 10:15:23] "POST /chat HTTP/1.1" 200 - [2.3s]
                                                                    ^^^^
                                                              Response time
```

If responses are slow (>5s), consider using a smaller model.

---

## Quick Start Commands (Copy-Paste)

### Morning startup (fresh start)
```bash
# Terminal 1
ollama serve

# Terminal 2 (wait 5 seconds after Terminal 1)
cd /path/to/emergency
python app.py

# Browser
# Open: http://localhost:8080
```

### After git pull
```bash
# Terminal 2 only (Ctrl+C, then:)
python app.py
```

### End of day shutdown
```bash
# Terminal 2: Ctrl+C
# Terminal 1: Ctrl+C
# Or just close both terminal windows
```

---

## Troubleshooting Checklist

If something isn't working:

- [ ] Is Ollama running? (`curl http://localhost:11434`)
- [ ] Is the Gemma model installed? (`ollama list`)
- [ ] Is Flask running? (`curl http://localhost:8080/health`)
- [ ] Are you on the right git branch? (`git branch`)
- [ ] Did you install dependencies? (`pip install -r requirements.txt`)
- [ ] Are there any errors in Terminal 1 or 2?
- [ ] Did you restart Flask after changing code?
- [ ] Is port 8080 available? (`lsof -i :8080`)

---

## Need Help?

- Check `OLLAMA_SETUP.md` for Ollama-specific issues
- Check `README.md` for general setup
- Check Flask terminal for error messages
- Check Ollama terminal for model loading issues
