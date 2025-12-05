#!/usr/bin/env python3
"""
Custom Lightweight NLP Chatbot for Emergency Shelter & First Aid
100% Offline - Simple keyword-based intent classification
Designed for India mountain areas with flood/disaster focus
"""

from typing import Dict, List, Tuple, Optional
from first_aid_knowledge import get_first_aid_info, format_first_aid_response


class EmergencyChatbot:
    """
    Lightweight chatbot with 3-tier intent classification:
    - Tier 1: Emergency (immediate action)
    - Tier 2: First Aid (medical help)
    - Tier 3: Information (preventive/general)
    """

    def __init__(self):
        """Initialize the chatbot with intent keywords."""

        # Tier 1: EMERGENCY - Immediate life-threatening situations
        self.tier1_emergency = {
            "severe_bleeding": {
                "keywords": ["severe bleeding", "heavy bleeding", "blood loss", "bleeding badly", "can't stop bleeding"],
                "priority": "CRITICAL",
                "response_type": "first_aid",
                "first_aid_query": "bleeding"
            },
            "heart_attack": {
                "keywords": ["heart attack", "chest pain severe", "crushing chest", "cardiac"],
                "priority": "CRITICAL",
                "response_type": "first_aid",
                "first_aid_query": "heart attack"
            },
            "stroke": {
                "keywords": ["stroke", "face drooping", "can't speak", "arm weak", "FAST"],
                "priority": "CRITICAL",
                "response_type": "first_aid",
                "first_aid_query": "stroke"
            },
            "not_breathing": {
                "keywords": ["not breathing", "stopped breathing", "no pulse", "unconscious"],
                "priority": "CRITICAL",
                "response_type": "first_aid",
                "first_aid_query": "cpr"
            },
            "choking": {
                "keywords": ["choking", "can't breathe", "something stuck throat"],
                "priority": "CRITICAL",
                "response_type": "first_aid",
                "first_aid_query": "choking"
            },
            "trapped_flood": {
                "keywords": ["trapped in flood", "stuck in water", "surrounded by water", "flood emergency"],
                "priority": "CRITICAL",
                "response_type": "emergency_flood"
            },
            "snake_bite": {
                "keywords": ["snake bite", "snake bit me", "bitten by snake", "cobra", "viper", "krait"],
                "priority": "CRITICAL",
                "response_type": "first_aid",
                "first_aid_query": "snake_bite"
            }
        }

        # Tier 2: FIRST AID - Medical help needed but not immediately life-threatening
        self.tier2_first_aid = {
            "cpr_learn": {
                "keywords": ["cpr", "how to do cpr", "learn cpr", "cpr steps", "cardiopulmonary"],
                "response_type": "first_aid",
                "first_aid_query": "cpr"
            },
            "bleeding": {
                "keywords": ["bleeding", "cut", "wound", "laceration", "blood"],
                "response_type": "first_aid",
                "first_aid_query": "bleeding"
            },
            "burns": {
                "keywords": ["burn", "burnt", "scald", "fire injury", "hot water"],
                "response_type": "first_aid",
                "first_aid_query": "burns"
            },
            "fracture": {
                "keywords": ["broken bone", "fracture", "bone break", "broken arm", "broken leg"],
                "response_type": "first_aid",
                "first_aid_query": "fracture"
            },
            "sprain": {
                "keywords": ["sprain", "twisted ankle", "twisted wrist", "swollen joint"],
                "response_type": "first_aid",
                "first_aid_query": "sprain"
            },
            "head_injury": {
                "keywords": ["head injury", "hit head", "head wound", "concussion"],
                "response_type": "first_aid",
                "first_aid_query": "head_injury"
            },
            "hypothermia": {
                "keywords": ["hypothermia", "too cold", "freezing", "shivering badly"],
                "response_type": "first_aid",
                "first_aid_query": "hypothermia"
            },
            "heat_stroke": {
                "keywords": ["heat stroke", "too hot", "overheating", "heat exhaustion"],
                "response_type": "first_aid",
                "first_aid_query": "heat_stroke"
            },
            "poisoning": {
                "keywords": ["poisoning", "poison", "swallowed", "toxic"],
                "response_type": "first_aid",
                "first_aid_query": "poisoning"
            },
            "allergic_reaction": {
                "keywords": ["allergic", "allergy", "anaphylaxis", "swelling", "hives", "rash"],
                "response_type": "first_aid",
                "first_aid_query": "allergic_reaction"
            },
            "shock": {
                "keywords": ["shock", "pale", "clammy", "weak pulse"],
                "response_type": "first_aid",
                "first_aid_query": "shock"
            }
        }

        # Tier 3: INFORMATION - Preventive and general information
        self.tier3_information = {
            "find_shelter": {
                "keywords": ["nearest shelter", "closest shelter", "find shelter", "shelter near me",
                           "where shelter", "safe place", "evacuation", "where to go"],
                "response_type": "shelter_location"
            },
            "list_shelters": {
                "keywords": ["show shelters", "all shelters", "list shelters", "shelter list"],
                "response_type": "shelter_list"
            },
            "flood_safety": {
                "keywords": ["flood safety", "what to do in flood", "what to do flood",
                           "flood survival", "flood tips", "during flood",
                           "monsoon flood", "flash flood", "water rising", "flood help"],
                "response_type": "first_aid",
                "first_aid_query": "flood_safety"
            },
            "flood_injuries": {
                "keywords": ["waterborne disease", "leptospirosis", "contaminated water",
                           "flood injury", "after flood", "water disease"],
                "response_type": "first_aid",
                "first_aid_query": "flood_injuries"
            },
            "mountain_emergency": {
                "keywords": ["altitude sickness", "altitude sick", "mountain sickness", "landslide",
                           "lost in mountain", "stranded", "mountain emergency", "high altitude",
                           "mountain help"],
                "response_type": "first_aid",
                "first_aid_query": "mountain_emergencies"
            },
            "emergency_numbers": {
                "keywords": ["emergency number", "emergency contact", "call who", "helpline",
                           "police number", "ambulance number", "who to call", "contact number",
                           "phone number emergency", "whom to call"],
                "response_type": "first_aid",
                "first_aid_query": "indian_emergency_numbers"
            },
            "disaster_preparedness": {
                "keywords": ["prepare", "preparation", "emergency kit", "what to pack",
                           "disaster kit", "ready", "supplies needed"],
                "response_type": "disaster_prep"
            },
            "first_aid_general": {
                "keywords": ["first aid", "medical help", "what is first aid", "first aid info"],
                "response_type": "first_aid_list"
            },
            "greet": {
                "keywords": ["hi", "hello", "hey", "help", "start", "namaste"],
                "response_type": "greeting"
            },
            "thanks": {
                "keywords": ["thank", "thanks", "thank you", "dhanyavaad"],
                "response_type": "thanks"
            }
        }

    def classify_intent(self, message: str) -> Tuple[str, Dict, int]:
        """
        Classify user message into intent using keyword matching.

        Args:
            message: User's message

        Returns:
            Tuple of (intent_name, intent_data, tier_level)
        """
        message_lower = message.lower()

        # Check Tier 1 (Emergency) first - highest priority
        for intent_name, intent_data in self.tier1_emergency.items():
            if any(keyword in message_lower for keyword in intent_data["keywords"]):
                return intent_name, intent_data, 1

        # Check Tier 2 (First Aid)
        for intent_name, intent_data in self.tier2_first_aid.items():
            if any(keyword in message_lower for keyword in intent_data["keywords"]):
                return intent_name, intent_data, 2

        # Check Tier 3 (Information)
        for intent_name, intent_data in self.tier3_information.items():
            if any(keyword in message_lower for keyword in intent_data["keywords"]):
                return intent_name, intent_data, 3

        # No match found
        return "unknown", {}, 0

    def generate_response(self, message: str, user_location: Optional[Dict] = None) -> List[Dict]:
        """
        Generate chatbot response based on user message.

        Args:
            message: User's message
            user_location: Optional dict with 'latitude' and 'longitude'

        Returns:
            List of response dictionaries
        """
        intent_name, intent_data, tier = self.classify_intent(message)

        # Handle unknown intent
        if tier == 0:
            return [{
                "text": self._get_default_help_message()
            }]

        response_type = intent_data.get("response_type")

        # Tier 1: Emergency responses
        if tier == 1:
            return self._handle_emergency(intent_name, intent_data, user_location)

        # Tier 2: First aid responses
        elif tier == 2:
            return self._handle_first_aid(intent_data)

        # Tier 3: Information responses
        elif tier == 3:
            return self._handle_information(intent_name, intent_data, user_location)

        return [{"text": "I couldn't process that request. Please try again."}]

    def _handle_emergency(self, intent_name: str, intent_data: Dict,
                         user_location: Optional[Dict]) -> List[Dict]:
        """Handle Tier 1 emergency intents."""
        responses = []

        # Add emergency alert
        responses.append({
            "text": f"🚨 **EMERGENCY DETECTED** 🚨\n\n"
                   f"**Immediately call:**\n"
                   f"📞 **108** - Emergency Ambulance (Free)\n"
                   f"📞 **102** - Ambulance\n"
                   f"📞 **100** - Police\n\n"
                   f"While waiting for help:"
        })

        # Handle specific emergency types
        if intent_data["response_type"] == "first_aid":
            first_aid_info = get_first_aid_info(intent_data["first_aid_query"])
            formatted = format_first_aid_response(first_aid_info)
            responses.append({"text": formatted})

        elif intent_data["response_type"] == "emergency_flood":
            responses.append({
                "text": "**FLOOD EMERGENCY - IMMEDIATE ACTIONS:**\n\n"
                       "1. **Call 1078** (Disaster Management) or **100** (Police) NOW\n"
                       "2. Move to HIGHEST point available (roof, upper floor, hill)\n"
                       "3. Avoid contact with floodwater if possible\n"
                       "4. Signal for help - wave bright cloth, use flashlight, shout\n"
                       "5. If water is rising fast, climb onto sturdy furniture or float on debris\n"
                       "6. DO NOT try to swim through fast-moving water\n\n"
                       "**Rescue teams are on the way. Stay visible and stay high.**"
            })

        # Add shelter location if available
        if user_location:
            responses.append({
                "text": "🏥 Finding nearest emergency shelter...",
                "custom": {"action": "find_nearest_shelter"}
            })
        else:
            responses.append({
                "text": "📍 Please share your location to find the nearest emergency shelter.",
                "custom": {"action": "request_location"}
            })

        return responses

    def _handle_first_aid(self, intent_data: Dict) -> List[Dict]:
        """Handle Tier 2 first aid intents."""
        first_aid_query = intent_data.get("first_aid_query")

        if first_aid_query:
            first_aid_info = get_first_aid_info(first_aid_query)
            formatted = format_first_aid_response(first_aid_info)

            # Add emergency number reminder for serious injuries
            if first_aid_query in ["bleeding", "burns", "fracture", "head_injury", "poisoning"]:
                prefix = "⚠️ **For serious injuries, call 108 (Emergency Ambulance) immediately**\n\n"
                formatted = prefix + formatted

            return [{"text": formatted}]

        return [{"text": "First aid information not available for this query."}]

    def _handle_information(self, intent_name: str, intent_data: Dict,
                           user_location: Optional[Dict]) -> List[Dict]:
        """Handle Tier 3 information intents."""
        response_type = intent_data.get("response_type")

        # Shelter location
        if response_type == "shelter_location":
            if user_location:
                return [{
                    "text": "🏥 Searching for nearest shelters...",
                    "custom": {"action": "find_nearest_shelter"}
                }]
            else:
                return [{
                    "text": "📍 To find the nearest shelter, I need your location.\n\n"
                           "Please click 'Get My Location' button or click on the map to set your location.",
                    "custom": {"action": "request_location"}
                }]

        # Shelter list
        elif response_type == "shelter_list":
            return [{
                "text": "📍 All available shelters are displayed on the map as colored markers:\n\n"
                       "🔴 Red - Schools\n"
                       "🔵 Blue - Police Stations\n"
                       "🟢 Green - Fire Stations\n\n"
                       "Click any marker to see details. Set your location to find the nearest one."
            }]

        # First aid list
        elif response_type == "first_aid_list":
            first_aid_info = get_first_aid_info("general")
            return [{"text": format_first_aid_response(first_aid_info)}]

        # First aid queries
        elif response_type == "first_aid":
            first_aid_query = intent_data.get("first_aid_query")
            if first_aid_query:
                first_aid_info = get_first_aid_info(first_aid_query)
                formatted = format_first_aid_response(first_aid_info)
                return [{"text": formatted}]

        # Disaster preparedness
        elif response_type == "disaster_prep":
            return [{"text": self._get_disaster_preparedness_info()}]

        # Greeting
        elif response_type == "greeting":
            return [{"text": self._get_greeting_message()}]

        # Thanks
        elif response_type == "thanks":
            return [{"text": "You're welcome! Stay safe. If you need any more help with shelters or first aid, just ask! 🙏"}]

        return [{"text": "I couldn't find information for that request."}]

    def _get_greeting_message(self) -> str:
        """Get greeting message."""
        return (
            "Namaste! 🙏 I'm your Emergency Assistant for mountain areas in India.\n\n"
            "**I can help you with:**\n\n"
            "🏥 **Find Shelters** - Nearest safe locations\n"
            "🩹 **First Aid** - CPR, bleeding, burns, fractures, snake bites\n"
            "🌊 **Flood Safety** - Survival tips and safety measures\n"
            "⛰️ **Mountain Emergencies** - Altitude sickness, landslides, getting lost\n"
            "📞 **Emergency Numbers** - Who to call in India\n"
            "🎒 **Disaster Preparedness** - How to prepare for emergencies\n\n"
            "**Emergency Numbers:**\n"
            "📞 108 - Emergency Ambulance (Free)\n"
            "📞 100 - Police\n"
            "📞 1078 - Disaster Management\n\n"
            "How can I help you today?"
        )

    def _get_default_help_message(self) -> str:
        """Get default help message for unknown intents."""
        return (
            "I'm not sure what you're asking for. Here's what I can help with:\n\n"
            "**Say things like:**\n"
            "• 'Find nearest shelter'\n"
            "• 'How to stop bleeding'\n"
            "• 'What to do in a flood'\n"
            "• 'Snake bite treatment'\n"
            "• 'Emergency numbers'\n"
            "• 'Mountain emergency'\n"
            "• 'First aid for burns'\n\n"
            "Or just say 'help' to see all options!"
        )

    def _get_disaster_preparedness_info(self) -> str:
        """Get disaster preparedness information."""
        return (
            "🎒 **Disaster Preparedness for Mountain Areas**\n\n"
            "**Emergency Kit Essentials:**\n\n"
            "**Survival Basics:**\n"
            "• Water: 3 liters per person per day (for 3 days minimum)\n"
            "• Food: Non-perishable items (biscuits, dry fruits, energy bars)\n"
            "• Water purification tablets (for monsoon floods)\n\n"
            "**First Aid:**\n"
            "• First aid kit with bandages, antiseptic, pain relievers\n"
            "• Prescription medications (1-week supply)\n"
            "• Snake bite information card\n\n"
            "**Communication & Light:**\n"
            "• Fully charged mobile phone + power bank\n"
            "• Flashlight with extra batteries\n"
            "• Whistle for signaling\n"
            "• Emergency contact list (written on paper)\n\n"
            "**Protection:**\n"
            "• Warm clothing (mountain nights are cold)\n"
            "• Waterproof jacket (monsoon essential)\n"
            "• Sturdy shoes/boots\n"
            "• Emergency blanket/sleeping bag\n\n"
            "**Documents (in waterproof bag):**\n"
            "• ID cards (Aadhaar, voter ID)\n"
            "• Important phone numbers\n"
            "• Medical information\n\n"
            "**For Floods:**\n"
            "• Keep kit on UPPER FLOOR, not basement\n"
            "• Know evacuation routes\n"
            "• Monitor weather warnings (IMD app)\n\n"
            "**For Mountains:**\n"
            "• Inform someone of your travel plans\n"
            "• Check weather before traveling\n"
            "• Avoid monsoon season travel (June-September) in high-risk areas\n\n"
            "**Emergency Numbers to Save:**\n"
            "📞 108, 100, 101, 102, 1078\n\n"
            "**Prepare NOW. Don't wait for disaster to strike!**"
        )


# Singleton instance
chatbot = EmergencyChatbot()


def process_message(message: str, user_location: Optional[Dict] = None) -> List[Dict]:
    """
    Process user message and return chatbot responses.

    Args:
        message: User's message
        user_location: Optional dict with 'latitude' and 'longitude'

    Returns:
        List of response dictionaries
    """
    return chatbot.generate_response(message, user_location)


if __name__ == "__main__":
    # Test the chatbot
    print("="*60)
    print("Emergency Chatbot - Testing")
    print("="*60)

    test_messages = [
        "hello",
        "nearest shelter",
        "how to stop bleeding",
        "snake bite",
        "what to do in flood",
        "emergency numbers",
        "altitude sickness",
        "heart attack",
        "prepare for disaster"
    ]

    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"USER: {msg}")
        print('='*60)
        responses = process_message(msg)
        for resp in responses:
            print(resp.get("text", ""))
            if "custom" in resp:
                print(f"[Action: {resp['custom']}]")
