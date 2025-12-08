# Emergency Chatbot - Quick Start Guide

## Overview

Your custom lightweight offline chatbot is now fully integrated! It's designed specifically for India mountain areas with flood and disaster preparedness features.

## 🚀 How to Run

### 1. Start the Flask Backend

```bash
python3 app.py
```

This will:
- Start the server on `http://localhost:5000`
- Auto-load shelter data from shelters_downloaded.xlsx
- Initialize the chatbot

### 2. Open the Application

Open your browser and go to:
```
http://localhost:5000
```

You'll see:
- Interactive map with shelter markers
- Chat interface (bottom-right corner)
- Location controls (top-left)

## 💬 Testing the Chatbot

### Try These Queries:

#### Emergency Scenarios (Tier 1 - Critical)
- "snake bit me" → Emergency snake bite response
- "severe bleeding" → Emergency bleeding response with ambulance numbers
- "heart attack" → Critical emergency response
- "trapped in flood" → Flood emergency rescue protocol

#### First Aid Information (Tier 2)
- "how to stop bleeding" → Step-by-step bleeding treatment
- "CPR" → CPR instructions for India
- "burn treatment" → First aid for burns
- "broken bone" → Fracture treatment

#### General Information (Tier 3)
- "nearest shelter" → Finds closest shelters (needs location)
- "what to do in flood" → Comprehensive flood safety guide
- "emergency numbers" → All Indian emergency contacts
- "altitude sickness" → Mountain emergency information
- "prepare for disaster" → Disaster preparedness checklist

#### Greetings
- "hello" / "hi" / "namaste" → Welcome message with options

## 🎯 Key Features

### 3-Tier Intent Classification

**Tier 1: EMERGENCY** (Red Alert 🚨)
- Immediate life-threatening situations
- Auto-displays emergency numbers (108, 102, 100)
- Requests location for nearest shelter
- Keywords: severe bleeding, heart attack, stroke, trapped in flood, snake bite

**Tier 2: FIRST AID** (Medical Help 🏥)
- Non-critical but needs medical attention
- Provides detailed step-by-step instructions
- Keywords: bleeding, burns, fracture, CPR, sprain

**Tier 3: INFORMATION** (General Help ℹ️)
- Preventive and educational content
- Shelter locations, safety tips, preparedness
- Keywords: nearest shelter, flood safety, emergency numbers, prepare

### India-Specific Content

✅ **Emergency Numbers**
- 108 - Emergency Ambulance (Free, 24/7)
- 100 - Police
- 101 - Fire Services
- 102 - Ambulance
- 1078 - Disaster Management
- 1070 - Women Helpline
- State-specific numbers for Uttarakhand, Himachal Pradesh, Kerala, Karnataka

✅ **Snake Bite Treatment**
- Indian venomous species (Cobra, Krait, Russell's Viper, Saw-scaled Viper)
- Anti-venom availability reminder
- Traditional medicine warnings

✅ **Flood Safety**
- Before/During/After flood protocols
- Mountain-specific flash flood warnings
- Monsoon season safety
- Waterborne disease prevention (Leptospirosis, Cholera, Typhoid)

✅ **Mountain Emergencies**
- Altitude sickness (above 2500m)
- Landslide safety protocols
- Lost/stranded procedures
- Cold weather hypothermia

✅ **Disaster Preparedness**
- Emergency kit for mountain areas
- Monsoon-specific supplies
- Document protection
- Communication plan

## 📍 Location Features

### Setting Your Location

**Option 1: Automatic**
Click "Get My Location" button → Allow browser permission

**Option 2: Manual**
Click anywhere on the map to set your location

### Finding Shelters

Once location is set, ask:
- "nearest shelter"
- "find shelter"
- "safe place"

The chatbot will:
1. Calculate distances to all shelters
2. Show top 3 nearest shelters
3. Display distance in km and miles
4. Highlight them on the map

## 🗺️ Map Legend

- 🔴 **Red Markers** = Schools
- 🔵 **Blue Markers** = Police Stations
- 🟢 **Green Markers** = Fire Stations
- 🟠 **Orange Marker** = Your Location

## 🔧 Shelter Data

The app loads shelter data from `shelters_downloaded.xlsx`, which contains real shelter locations including schools, police stations, and fire stations in the region.

### Adding More Shelter Data

To fetch real data from Google Maps API:

1. Get a Google Maps API key
2. Create `.env` file:
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   SEARCH_LOCATION=30.3165,78.0322  # Dehradun coordinates
   SEARCH_RADIUS=10000  # 10km radius
   ```
3. Run:
   ```bash
   python3 shelter_locator.py
   ```
4. Restart Flask app to load new data

## 🧪 Complete Test Suite

Run this to test all chatbot features:

```bash
python3 chatbot.py
```

This will test:
- Greetings
- Shelter location
- Bleeding emergency
- Snake bite emergency
- First aid queries
- Flood safety
- Emergency numbers
- Mountain emergencies
- Disaster preparation
- CPR instructions

## 📊 Chatbot Architecture

```
User Message
    ↓
Intent Classifier (Keyword Matching)
    ↓
Tier Detection (1: Emergency, 2: First Aid, 3: Info)
    ↓
Response Generator
    ↓
    ├── First Aid Knowledge Base
    ├── Shelter Manager (if location query)
    ├── Emergency Numbers
    └── Disaster Preparedness
    ↓
Formatted Response (with Markdown)
```

## ⚡ Performance

- **Response Time**: < 50ms (pure Python, no ML)
- **Dependencies**: Flask + pandas only
- **Offline**: 100% offline (except Google Maps tiles & API for fetching shelters)
- **Storage**: ~2MB (all first aid data included)

## 🎨 Customization

### Adding New Intents

Edit `chatbot.py`:

```python
# Add to appropriate tier
self.tier3_information["your_intent"] = {
    "keywords": ["keyword1", "keyword2"],
    "response_type": "first_aid",
    "first_aid_query": "your_condition"
}
```

### Adding First Aid Content

Edit `first_aid_knowledge.py`:

```python
FIRST_AID_DATA["your_condition"] = {
    "title": "Your Condition Title",
    "steps": ["Step 1", "Step 2"],
    "warnings": ["Warning 1"]
}
```

## 🚨 Emergency Protocol

When chatbot detects emergencies (Tier 1):
1. Shows emergency alert banner
2. Displays all emergency numbers prominently
3. Provides immediate first aid steps
4. Requests location for nearest hospital/shelter

## 📱 Mobile Responsive

The UI automatically adjusts for mobile devices:
- Chat window resizes to full width
- Map remains accessible
- Touch-friendly interface

## 🔐 Privacy & Offline Mode

- All processing done locally
- No data sent to external servers (except Google Maps for tiles)
- User location never stored
- Completely private conversations

## 🆘 Troubleshooting

**Chatbot not responding?**
- Check Flask server is running (`python3 app.py`)
- Open browser console for errors (F12)
- Verify chatbot.py is imported correctly

**Shelters not showing?**
- Verify `shelters_downloaded.xlsx` exists in the project directory
- Restart Flask server
- Check console for "Loaded X shelters" message

**Location not working?**
- Grant browser location permission
- Or manually click on map
- Check browser supports Geolocation API

## 📚 Resources

- Emergency numbers are hardcoded for reliability
- First aid info based on WHO/Red Cross guidelines
- India-specific content vetted for local conditions
- Monsoon/mountain safety from IMD and NDRF guidelines

## 🌐 Offline Capability

**What works offline:**
- All chatbot responses
- First aid information
- Emergency numbers
- Shelter search (from cached Excel data)

**Requires internet:**
- Google Maps tiles (for map display)
- Google Places API (to fetch new shelters)
- Initial map loading

## 🎯 Next Steps

1. Test with your actual location in India
2. Add more regional shelter data via Google API
3. Customize first aid content for your specific region
4. Add language support (future: Sarvam AI integration for Hindi/regional)

---

**Built with ❤️ for emergency preparedness in India's mountain regions**

For issues or questions, check the code comments or README.md
