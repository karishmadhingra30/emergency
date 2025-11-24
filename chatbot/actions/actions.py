"""
Custom Rasa Actions for Emergency Chatbot
Handles shelter location queries and first aid information requests.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import sys
import os

# Add parent directory to path to import first_aid_knowledge
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from first_aid_knowledge import get_first_aid_info, format_first_aid_response


class ActionFindNearestShelter(Action):
    """Action to find and return nearest shelter information."""

    def name(self) -> Text:
        return "action_find_nearest_shelter"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get user's location from slots if available
        user_lat = tracker.get_slot("user_latitude")
        user_lon = tracker.get_slot("user_longitude")

        if user_lat and user_lon:
            # User has provided location - trigger backend API call
            response = (
                f"📍 I'll find the nearest shelter to your location "
                f"({user_lat}, {user_lon}).\n\n"
                f"Calculating distance to nearby shelters..."
            )
            dispatcher.utter_message(text=response)

            # Send event to frontend to trigger shelter calculation
            dispatcher.utter_message(json_message={
                "action": "find_nearest_shelter",
                "latitude": user_lat,
                "longitude": user_lon
            })
        else:
            # User hasn't provided location - request it
            response = (
                "📍 To find the nearest shelter, I need your current location.\n\n"
                "**Options:**\n"
                "1. Click 'Get My Location' on the map\n"
                "2. Click on the map where you are\n"
                "3. Tell me your coordinates\n\n"
                "Once I have your location, I'll find the closest shelter for you."
            )
            dispatcher.utter_message(text=response)

            # Send event to frontend to request location
            dispatcher.utter_message(json_message={
                "action": "request_location"
            })

        return []


class ActionProvideFirstAid(Action):
    """Action to provide first aid information."""

    def name(self) -> Text:
        return "action_provide_first_aid"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user's message
        user_message = tracker.latest_message.get('text', '')

        # Check if user specified an injury type
        injury_type = tracker.get_slot("injury_type")

        if injury_type:
            query = injury_type
        else:
            query = user_message

        # Get first aid information
        first_aid_info = get_first_aid_info(query)

        if first_aid_info.get("found"):
            # Format and send the response
            response = format_first_aid_response(first_aid_info)
            dispatcher.utter_message(text=response)

            # Also send structured data to frontend
            dispatcher.utter_message(json_message={
                "action": "first_aid_info",
                "condition": first_aid_info["condition"],
                "info": first_aid_info["info"]
            })
        else:
            # No specific match - ask for clarification
            dispatcher.utter_message(text=first_aid_info.get("message"))

            # Send list of available topics to frontend
            dispatcher.utter_message(json_message={
                "action": "first_aid_topics",
                "topics": [
                    "Bleeding", "Burns", "CPR", "Fractures", "Choking",
                    "Shock", "Head Injuries", "Heat Stroke", "Hypothermia",
                    "Heart Attack", "Stroke", "Poisoning", "Snake Bites",
                    "Allergic Reactions", "Sprains"
                ]
            })

        return []


class ActionSetUserLocation(Action):
    """Action to set user's location in slots."""

    def name(self) -> Text:
        return "action_set_user_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract entities
        entities = tracker.latest_message.get("entities", [])

        latitude = None
        longitude = None

        for entity in entities:
            if entity["entity"] == "latitude":
                try:
                    latitude = float(entity["value"])
                except:
                    pass
            elif entity["entity"] == "longitude":
                try:
                    longitude = float(entity["value"])
                except:
                    pass

        if latitude and longitude:
            dispatcher.utter_message(
                text=f"✓ Location received: ({latitude}, {longitude})"
            )
            return [
                SlotSet("user_latitude", latitude),
                SlotSet("user_longitude", longitude)
            ]
        else:
            dispatcher.utter_message(
                text="I couldn't understand those coordinates. Please try again."
            )
            return []
