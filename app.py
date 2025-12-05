#!/usr/bin/env python3
"""
Flask Backend for Emergency Shelter and Chatbot Application
Lightweight custom chatbot with shelter location services.
"""

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import pandas as pd
import os
import math
from typing import List, Dict, Optional
import json
from chatbot import process_message

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
SHELTER_DATA_FILE = None  # Will be set dynamically


class ShelterManager:
    """Manages shelter data and distance calculations."""

    def __init__(self, excel_file: Optional[str] = None):
        """Initialize with shelter data from Excel file."""
        self.shelters = []
        if excel_file and os.path.exists(excel_file):
            self.load_shelters_from_excel(excel_file)

    def load_shelters_from_excel(self, excel_file: str):
        """Load shelter data from Excel file."""
        try:
            df = pd.read_excel(excel_file)
            print(f"Loaded {len(df)} shelters from {excel_file}")

            for _, row in df.iterrows():
                self.shelters.append({
                    'name': str(row.get('name', 'Unknown')),
                    'type': str(row.get('type', 'Unknown')),
                    'latitude': float(row.get('latitude', 0)),
                    'longitude': float(row.get('longitude', 0)),
                    'address': str(row.get('address', 'N/A')),
                    'rating': row.get('rating', 'N/A'),
                    'operational_status': str(row.get('operational_status', 'UNKNOWN'))
                })
        except Exception as e:
            print(f"Error loading shelter data: {e}")

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def find_nearest_shelters(self, user_lat: float, user_lon: float,
                            limit: int = 5) -> List[Dict]:
        """
        Find nearest shelters to user's location.

        Args:
            user_lat: User's latitude
            user_lon: User's longitude
            limit: Maximum number of shelters to return

        Returns:
            List of nearest shelters with distance information
        """
        if not self.shelters:
            return []

        # Calculate distances
        shelters_with_distance = []
        for shelter in self.shelters:
            distance = self.calculate_distance(
                user_lat, user_lon,
                shelter['latitude'], shelter['longitude']
            )
            shelter_copy = shelter.copy()
            shelter_copy['distance_km'] = round(distance, 2)
            shelter_copy['distance_miles'] = round(distance * 0.621371, 2)
            shelters_with_distance.append(shelter_copy)

        # Sort by distance
        shelters_with_distance.sort(key=lambda x: x['distance_km'])

        # Return top N
        return shelters_with_distance[:limit]


# Initialize shelter manager
shelter_manager = ShelterManager()


@app.route('/')
def index():
    """Serve the main map page with chatbot."""
    return send_file('map_with_chat.html')


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages with custom lightweight NLP.

    Expected JSON: {"message": "user message", "sender": "user_id", "location": {"latitude": float, "longitude": float} (optional)}
    """
    try:
        data = request.json
        user_message = data.get('message', '')
        sender = data.get('sender', 'user')
        user_location = data.get('location')  # Optional: {"latitude": float, "longitude": float}

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Process message through chatbot
        bot_responses = process_message(user_message, user_location)

        return jsonify({
            'success': True,
            'responses': bot_responses
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/nearest-shelter', methods=['POST'])
def nearest_shelter():
    """
    Find nearest shelter based on user's location.

    Expected JSON: {"latitude": float, "longitude": float, "limit": int (optional)}
    """
    try:
        data = request.json
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        limit = data.get('limit', 5)

        if user_lat is None or user_lon is None:
            return jsonify({'error': 'Latitude and longitude required'}), 400

        # Find nearest shelters
        nearest = shelter_manager.find_nearest_shelters(
            float(user_lat),
            float(user_lon),
            limit
        )

        if not nearest:
            return jsonify({
                'success': False,
                'message': 'No shelters found. Please load shelter data first.'
            })

        return jsonify({
            'success': True,
            'nearest_shelters': nearest,
            'user_location': {
                'latitude': user_lat,
                'longitude': user_lon
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/load-shelters', methods=['POST'])
def load_shelters():
    """
    Load shelter data from Excel file.

    Expected JSON: {"file_path": "path/to/excel.xlsx"}
    """
    try:
        data = request.json
        file_path = data.get('file_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 400

        shelter_manager.load_shelters_from_excel(file_path)

        return jsonify({
            'success': True,
            'message': f'Loaded {len(shelter_manager.shelters)} shelters',
            'shelter_count': len(shelter_manager.shelters)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/shelters', methods=['GET'])
def get_all_shelters():
    """Get all loaded shelter data."""
    return jsonify({
        'success': True,
        'shelters': shelter_manager.shelters,
        'count': len(shelter_manager.shelters)
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'chatbot': 'custom_lightweight',
        'shelter_count': len(shelter_manager.shelters)
    })


def find_latest_shelter_file():
    """Find the most recent shelter Excel file."""
    files = [f for f in os.listdir('.') if f.startswith('shelters_') and f.endswith('.xlsx')]
    if files:
        files.sort(reverse=True)  # Most recent first
        return files[0]
    return None


if __name__ == '__main__':
    # Try to auto-load shelter data
    shelter_file = find_latest_shelter_file()
    if shelter_file:
        print(f"Auto-loading shelter data from: {shelter_file}")
        shelter_manager.load_shelters_from_excel(shelter_file)
    else:
        print("No shelter data file found. You can load it via /load-shelters endpoint.")

    print("\n" + "="*60)
    print("Emergency Shelter Chatbot Backend")
    print("="*60)
    print(f"Flask server: http://localhost:5000")
    print(f"Chatbot: Custom Lightweight NLP")
    print(f"Shelters loaded: {len(shelter_manager.shelters)}")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
