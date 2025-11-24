# Emergency Shelter Chatbot - Setup Guide

## 🎯 Overview

This project integrates an **offline AI chatbot** using Rasa into the emergency shelter application. The chatbot helps users:
- 🏥 Find the nearest shelter location
- 🩹 Get first aid information for emergencies
- 📍 Navigate emergency locations on an interactive map

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Frontend (HTML/JS/Leaflet)       │
│   - Interactive map                 │
│   - Chat interface                  │
└──────────────┬──────────────────────┘
               │
               ↓ (REST API)
┌──────────────────────────────────────┐
│   Flask Backend (Port 5000)          │
│   - Shelter location calculation     │
│   - First aid knowledge base         │
│   - API endpoints                    │
└──────────────┬───────────────────────┘
               │
               ↓ (Webhooks)
┌──────────────────────────────────────┐
│   Rasa Server (Port 5005)            │
│   - NLP intent classification        │
│   - Dialog management                │
│   - Offline AI processing            │
└──────────────┬───────────────────────┘
               │
               ↓ (Actions)
┌──────────────────────────────────────┐
│   Rasa Actions (Port 5055)           │
│   - Custom actions                   │
│   - Business logic                   │
└──────────────────────────────────────┘
```

## 📁 Project Structure

```
emergency/
├── chatbot/                    # Rasa chatbot files
│   ├── config.yml             # Rasa NLP pipeline config
│   ├── domain.yml             # Chatbot domain (intents, actions)
│   ├── endpoints.yml          # Rasa endpoints config
│   ├── data/
│   │   ├── nlu.yml           # Training data for intents
│   │   ├── stories.yml       # Conversation flows
│   │   └── rules.yml         # Conversation rules
│   ├── actions/
│   │   ├── actions.py        # Custom Rasa actions
│   │   └── __init__.py
│   └── models/               # Trained Rasa models (auto-generated)
│
├── app.py                     # Flask backend server
├── first_aid_knowledge.py     # First aid information database
├── map_with_chat.html         # Main UI with map and chat
│
├── shelter_locator.py         # Original shelter fetcher
├── offline_map_plotter.py     # Original map plotter
│
├── start_chatbot.sh          # Start all services
├── stop_chatbot.sh           # Stop all services
│
├── requirements.txt           # Python dependencies
└── CHATBOT_README.md         # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Rasa installation may take 5-10 minutes as it includes many ML dependencies.

### 2. Generate Shelter Data (if not already done)

```bash
# Create .env file with your Google Maps API key
echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env

# Fetch shelter locations
python shelter_locator.py
```

This will create a `shelters_YYYYMMDD_HHMMSS.xlsx` file with shelter locations.

### 3. Train the Rasa Model (First Time Only)

```bash
cd chatbot
rasa train
cd ..
```

This creates a trained model in `chatbot/models/`. Training takes 2-5 minutes.

### 4. Start All Services

**Option A: Using the startup script (Recommended)**

```bash
./start_chatbot.sh
```

This automatically starts:
- Rasa Actions Server (port 5055)
- Rasa Server (port 5005)
- Flask Backend (port 5000)

**Option B: Manual startup (for debugging)**

Open 3 separate terminals:

```bash
# Terminal 1: Start Rasa Actions
cd chatbot
rasa run actions --port 5055

# Terminal 2: Start Rasa Server
cd chatbot
rasa run --enable-api --cors "*" --port 5005

# Terminal 3: Start Flask Backend
python app.py
```

### 5. Access the Application

Open your browser to: **http://localhost:5000**

You should see:
- 🗺️ Interactive map with shelter locations
- 💬 Chat interface in the bottom-right corner

## 💬 Using the Chatbot

### Example Conversations

**Finding Nearest Shelter:**
```
User: "Where is the nearest shelter?"
Bot: "To find the nearest shelter, I'll need your location..."
[Click "Get My Location" or click on the map]
Bot: "Nearest Shelters:
     1. PS 123 School - 0.5 km away
     2. Central Police Station - 1.2 km away
     ..."
```

**Getting First Aid Information:**
```
User: "How do I treat bleeding?"
Bot: "🏥 How to Stop Bleeding
     Steps:
     1. Apply direct pressure with a clean cloth...
     2. Maintain pressure for 10-15 minutes...
     ..."
```

**Other Queries:**
- "Show me shelters"
- "CPR instructions"
- "What to do for burns"
- "First aid for fractures"
- "Help with heart attack"

## 🎓 Chatbot Capabilities

### Intents Supported

1. **greet** - Hello, hi, help
2. **ask_shelter_location** - Show shelters, where are shelters
3. **ask_nearest_shelter** - Nearest shelter, closest safe place
4. **ask_first_aid** - First aid, treating wounds, CPR, etc.
5. **thanks** - Thank you
6. **goodbye** - Bye, goodbye

### First Aid Topics

The chatbot can provide detailed first aid instructions for:

- 🩸 Bleeding and wounds
- 🔥 Burns
- ❤️ CPR
- 🦴 Fractures (broken bones)
- 🚨 Choking
- 💫 Shock
- 🧠 Head injuries
- ☀️ Heat stroke
- ❄️ Hypothermia
- ❤️‍🩹 Heart attack
- 🧠 Stroke
- ☠️ Poisoning
- 🐍 Snake bites
- 🤧 Allergic reactions
- 🦶 Sprains

## 🛠️ Customization

### Adding New First Aid Topics

Edit `first_aid_knowledge.py`:

```python
FIRST_AID_DATA = {
    "your_new_topic": {
        "title": "Your Topic Title",
        "steps": [
            "Step 1...",
            "Step 2..."
        ],
        "warnings": [
            "⚠️ Warning 1..."
        ]
    }
}
```

Then update the keyword mapping in `get_first_aid_info()`.

### Adding New Intents

1. **Add training examples** in `chatbot/data/nlu.yml`:
```yaml
- intent: your_new_intent
  examples: |
    - example query 1
    - example query 2
```

2. **Update domain** in `chatbot/domain.yml`:
```yaml
intents:
  - your_new_intent

actions:
  - action_your_new_action
```

3. **Create custom action** in `chatbot/actions/actions.py`:
```python
class ActionYourNewAction(Action):
    def name(self) -> Text:
        return "action_your_new_action"

    def run(self, dispatcher, tracker, domain):
        # Your logic here
        dispatcher.utter_message(text="Response")
        return []
```

4. **Retrain the model**:
```bash
cd chatbot
rasa train
```

### Modifying the UI

Edit `map_with_chat.html` to customize:
- Colors and styling (CSS section)
- Chat bubble appearance
- Map markers and colors
- Layout and positioning

## 🐛 Troubleshooting

### Issue: "Cannot connect to Rasa server"

**Solution:**
```bash
# Check if Rasa is running
curl http://localhost:5005

# If not, start it
cd chatbot
rasa run --enable-api --cors "*" --port 5005
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find and kill process using the port (e.g., 5005)
lsof -ti:5005 | xargs kill

# Or use the stop script
./stop_chatbot.sh
```

### Issue: "No shelters found"

**Solution:**
- Make sure you've run `shelter_locator.py` to fetch shelter data
- Check that the Excel file exists in the project directory
- Flask backend auto-loads the most recent `shelters_*.xlsx` file

### Issue: Chatbot gives generic responses

**Solution:**
- The model may need retraining with more examples
- Check logs in `logs/rasa_server.log` for intent classification
- Add more training examples for that intent in `chatbot/data/nlu.yml`

### Issue: Actions not working

**Solution:**
```bash
# Check if actions server is running
curl http://localhost:5055/health

# Check logs
cat logs/rasa_actions.log

# Restart actions server
cd chatbot
rasa run actions --port 5055
```

## 📊 Testing the System

### Test Rasa Server

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "hello"
  }'
```

### Test Flask Backend

```bash
# Health check
curl http://localhost:5000/health

# Get shelters
curl http://localhost:5000/shelters

# Find nearest shelter
curl -X POST http://localhost:5000/nearest-shelter \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

## 🔒 Offline Capability

The chatbot runs **completely offline** once set up:

✅ **Offline Components:**
- Rasa NLP engine (offline AI)
- Flask backend
- First aid knowledge base
- Interactive map (after initial tile loading)

⚠️ **Requires Internet:**
- Initial map tile loading (tiles are cached)
- Google Maps API for fetching shelter data (one-time setup)

For fully offline operation:
1. Fetch shelter data while online
2. Access the application - map tiles will be cached
3. Disconnect from internet
4. Application will continue to work with cached data

## 🚦 System Status

Check if all services are running:

```bash
# Rasa Server
curl http://localhost:5005/

# Rasa Actions
curl http://localhost:5055/health

# Flask Backend
curl http://localhost:5000/health
```

## 📝 Logs

All logs are saved in the `logs/` directory:

```bash
# View Flask logs
tail -f logs/flask.log

# View Rasa server logs
tail -f logs/rasa_server.log

# View Rasa actions logs
tail -f logs/rasa_actions.log
```

## 🛑 Stopping the Application

```bash
./stop_chatbot.sh
```

Or manually:
```bash
# Kill processes by port
kill $(lsof -ti:5000)  # Flask
kill $(lsof -ti:5005)  # Rasa
kill $(lsof -ti:5055)  # Actions
```

## 🎯 Next Steps / Future Enhancements

- [ ] Add voice input/output for hands-free operation
- [ ] Implement user location tracking
- [ ] Add more emergency scenarios (earthquake, flood, etc.)
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Save user history and preferences
- [ ] Integration with emergency services APIs
- [ ] Offline map tile storage for full offline mode
- [ ] SMS/text-based interface for no-internet scenarios

## 📞 Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Ensure all ports (5000, 5005, 5055) are available
3. Verify all dependencies are installed
4. Retrain the Rasa model if needed

## 📄 License

This project is for emergency use and educational purposes.

---

**Built with:**
- 🤖 [Rasa](https://rasa.com/) - Open source conversational AI
- 🌐 [Flask](https://flask.palletsprojects.com/) - Python web framework
- 🗺️ [Leaflet](https://leafletjs.com/) - Interactive map library
- 📊 [Pandas](https://pandas.pydata.org/) - Data analysis

**Stay Safe! 🏥**
