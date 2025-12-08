#!/usr/bin/env python3
"""
Gemma 3 Chatbot Wrapper via Ollama
Provides crisis first-aid assistance for India mountain emergencies
"""

import ollama
from typing import List, Dict, Optional
from first_aid_knowledge import FIRST_AID_DATA


class GemmaEmergencyChat:
    """
    Gemma 3 powered emergency chatbot with knowledge retrieval.
    """

    def __init__(self, model_name: str = "gemma2:2b"):
        """
        Initialize Gemma chatbot.

        Args:
            model_name: Ollama model name (default: gemma2:2b for efficiency)
        """
        self.model_name = model_name
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Gemma."""
        return """You are an Emergency Medical Assistant specialized in crisis first-aid for mountain and flood emergencies in India.

**Your Role:**
- Provide immediate, actionable first-aid guidance
- Emphasize calling emergency services (108, 100, 1078) for serious situations
- Give clear, step-by-step instructions
- Be concise but thorough
- Adapt to India-specific context (monsoon floods, mountain terrain, local emergency numbers)

**Critical Rules:**
1. ALWAYS recommend calling emergency services (108) for life-threatening situations
2. Provide science-based medical advice only - NO traditional remedies for emergencies
3. Be clear about when professional medical help is required
4. For shelter queries, acknowledge that you'll help find nearest locations
5. Keep responses practical and action-oriented

**Context:** You're assisting people in mountain regions of India during potential flood, landslide, or altitude emergencies.

Be compassionate but direct. Lives may depend on your guidance."""

    def retrieve_relevant_knowledge(self, user_message: str, top_k: int = 3) -> List[str]:
        """
        Simple keyword-based retrieval from first aid knowledge base.

        Args:
            user_message: User's query
            top_k: Maximum number of knowledge chunks to retrieve

        Returns:
            List of relevant knowledge chunks
        """
        message_lower = user_message.lower()
        relevant_chunks = []

        # Define keyword mappings to first aid data
        keyword_mappings = {
            "bleeding": ["bleeding", "blood", "cut", "wound"],
            "burns": ["burn", "burnt", "scald", "fire"],
            "cpr": ["cpr", "not breathing", "unconscious", "cardiac"],
            "fracture": ["fracture", "broken", "bone break"],
            "choking": ["choking", "can't breathe", "throat"],
            "shock": ["shock", "pale", "clammy"],
            "head_injury": ["head injury", "concussion", "hit head"],
            "heat_stroke": ["heat stroke", "overheating", "too hot"],
            "hypothermia": ["hypothermia", "cold", "freezing"],
            "heart_attack": ["heart attack", "chest pain"],
            "stroke": ["stroke", "face drooping", "FAST"],
            "poisoning": ["poison", "toxic", "swallowed"],
            "snake_bite": ["snake", "bite", "cobra", "krait", "viper"],
            "allergic_reaction": ["allergic", "allergy", "anaphylaxis", "swelling"],
            "sprain": ["sprain", "twisted", "ankle"],
            "flood_safety": ["flood", "water rising", "flash flood", "monsoon"],
            "flood_injuries": ["waterborne", "leptospirosis", "contaminated water"],
            "mountain_emergencies": ["altitude", "landslide", "lost", "stranded", "mountain"],
            "indian_emergency_numbers": ["emergency number", "helpline", "who to call", "ambulance number"]
        }

        # Find matching topics
        matched_topics = []
        for topic, keywords in keyword_mappings.items():
            if any(keyword in message_lower for keyword in keywords):
                matched_topics.append(topic)

        # Retrieve data for matched topics
        for topic in matched_topics[:top_k]:
            if topic in FIRST_AID_DATA:
                data = FIRST_AID_DATA[topic]
                chunk = self._format_knowledge_chunk(topic, data)
                relevant_chunks.append(chunk)

        return relevant_chunks

    def _format_knowledge_chunk(self, topic: str, data: Dict) -> str:
        """Format a knowledge chunk for context."""
        formatted = f"**{data.get('title', topic)}**\n"

        if "steps" in data:
            formatted += "\nSteps:\n"
            for step in data["steps"][:5]:  # Limit to first 5 steps to save tokens
                formatted += f"- {step}\n"

        if "warnings" in data:
            formatted += "\nWarnings:\n"
            for warning in data["warnings"][:3]:  # Limit warnings
                formatted += f"- {warning}\n"

        if "indian_species" in data:  # For snake bites
            formatted += "\nCommon in India:\n"
            for species in data["indian_species"][:4]:
                formatted += f"- {species}\n"

        if "numbers" in data:  # For emergency numbers
            formatted += "\n"
            for number in data["numbers"][:10]:
                formatted += f"{number}\n"

        return formatted

    def chat(self, user_message: str, user_location: Optional[Dict] = None) -> str:
        """
        Process user message and generate response using Gemma.

        Args:
            user_message: User's message
            user_location: Optional dict with 'latitude' and 'longitude'

        Returns:
            Chatbot response string
        """
        # Retrieve relevant knowledge
        knowledge_chunks = self.retrieve_relevant_knowledge(user_message)

        # Build context
        context = ""
        if knowledge_chunks:
            context = "\n**Relevant First Aid Knowledge:**\n\n"
            context += "\n\n".join(knowledge_chunks)
            context += "\n\n---\n\n"

        # Add location context
        location_context = ""
        if user_location:
            location_context = f"\nUser's location: Latitude {user_location.get('latitude')}, Longitude {user_location.get('longitude')}\n"

        # Construct full prompt
        user_prompt = f"{location_context}User Question: {user_message}\n\n{context}Please provide a clear, actionable response."

        try:
            # Call Gemma via Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': self.system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ]
            )

            return response['message']['content']

        except Exception as e:
            # Fallback error message
            error_msg = f"I'm having trouble connecting to the AI model. Error: {str(e)}\n\n"
            error_msg += "**Emergency Numbers (India):**\n"
            error_msg += "📞 108 - Emergency Ambulance (Free)\n"
            error_msg += "📞 100 - Police\n"
            error_msg += "📞 1078 - Disaster Management\n\n"

            # If we have knowledge chunks, include them as fallback
            if knowledge_chunks:
                error_msg += "Here's some relevant information from our knowledge base:\n\n"
                error_msg += "\n\n".join(knowledge_chunks)

            return error_msg


# Singleton instance
_gemma_chat = None

def get_gemma_chat(model_name: str = "gemma2:2b") -> GemmaEmergencyChat:
    """Get or create Gemma chat instance."""
    global _gemma_chat
    if _gemma_chat is None:
        _gemma_chat = GemmaEmergencyChat(model_name)
    return _gemma_chat


def gemma_chat(user_message: str, user_location: Optional[Dict] = None,
               model_name: str = "gemma2:2b") -> List[Dict]:
    """
    Main entry point for Gemma chatbot - compatible with existing chat interface.

    Args:
        user_message: User's message
        user_location: Optional dict with 'latitude' and 'longitude'
        model_name: Ollama model name

    Returns:
        List of response dictionaries (for compatibility with existing interface)
    """
    # Check if user is asking for nearest shelters
    message_lower = user_message.lower()
    shelter_keywords = ['nearest shelter', 'find shelter', 'closest shelter', 'shelter near',
                       'where is shelter', 'emergency shelter', 'shelters nearby']

    if any(keyword in message_lower for keyword in shelter_keywords):
        if not user_location:
            return [{"text": "📍 To find the nearest shelters, I need your location coordinates. Please provide them in the format: Latitude, Longitude (e.g., 30.324329, 78.0418)"}]

        # Import here to avoid circular dependency
        from app import shelter_manager

        # Find nearest shelters
        nearest_shelters = shelter_manager.find_nearest_shelters(
            user_location.get('latitude'),
            user_location.get('longitude'),
            limit=5
        )

        if not nearest_shelters:
            return [{"text": "I couldn't find any shelters in the database. Please contact emergency services at 108 (India Emergency Number)."}]

        # Format response
        response = "🏥 **Nearest Shelters** (ordered by distance):\n\n"
        for idx, shelter in enumerate(nearest_shelters, 1):
            response += f"**{idx}. {shelter['name']}**\n"
            response += f"   📍 Distance: {shelter['distance_km']} km ({shelter['distance_miles']} miles)\n"
            response += f"   🏢 Type: {shelter['type'].replace('_', ' ').title()}\n"
            response += f"   📮 Address: {shelter['address']}\n"
            response += f"   📊 Status: {shelter['operational_status']}\n\n"

        response += "**Important Emergency Numbers (India):**\n"
        response += "📞 108 - Emergency Ambulance (Free)\n"
        response += "📞 100 - Police\n"
        response += "📞 1078 - Disaster Management"

        return [{"text": response}]

    # For non-shelter queries, use Gemma chatbot
    chatbot = get_gemma_chat(model_name)
    response_text = chatbot.chat(user_message, user_location)

    # Return in same format as old chatbot for compatibility
    return [{"text": response_text}]


if __name__ == "__main__":
    # Test the chatbot
    print("="*60)
    print("Gemma Emergency Chatbot - Testing")
    print("="*60)

    test_messages = [
        "What should I do for severe bleeding?",
        "Snake bite treatment",
        "What to do in a flood?",
        "Emergency numbers in India",
        "Altitude sickness symptoms"
    ]

    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"USER: {msg}")
        print('='*60)
        try:
            responses = gemma_chat(msg)
            for resp in responses:
                print(resp.get("text", ""))
        except Exception as e:
            print(f"Error: {e}")
