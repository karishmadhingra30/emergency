#!/usr/bin/env python3
"""
Crisis Shelter Locator
Fetches potential shelter locations (schools, police stations, fire stations)
from Google Maps Places API and exports to Excel.
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv


class ShelterLocator:
    """Fetches and manages shelter location data from Google Maps Places API."""

    PLACE_TYPES = {
        'schools': 'school',
        'police_stations': 'police',
        'fire_stations': 'fire_station'
    }

    def __init__(self, api_key: str, location: str, radius: int = 5000):
        """
        Initialize the ShelterLocator.

        Args:
            api_key: Google Maps API key
            location: Center point for search (lat,lng format, e.g., "40.7128,-74.0060")
            radius: Search radius in meters (default: 5000m = 5km)
        """
        self.api_key = api_key
        self.location = location
        self.radius = radius
        self.base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.all_shelters = []

    def fetch_places(self, place_type: str, type_label: str) -> List[Dict]:
        """
        Fetch places of a specific type from Google Maps API.

        Args:
            place_type: Google Places API type (e.g., 'school', 'police')
            type_label: Human-readable label for the type

        Returns:
            List of place dictionaries
        """
        places = []
        params = {
            'location': self.location,
            'radius': self.radius,
            'type': place_type,
            'key': self.api_key
        }

        next_page_token = None

        while True:
            if next_page_token:
                params['pagetoken'] = next_page_token
                # Google requires a short delay before using next_page_token
                import time
                time.sleep(2)

            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data['status'] != 'OK' and data['status'] != 'ZERO_RESULTS':
                    print(f"Warning: API returned status {data['status']} for {type_label}")
                    if data['status'] == 'REQUEST_DENIED':
                        print(f"Error message: {data.get('error_message', 'No error message')}")
                    break

                results = data.get('results', [])
                print(f"Found {len(results)} {type_label} in this batch")

                for place in results:
                    places.append({
                        'name': place.get('name', 'Unknown'),
                        'type': type_label,
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'address': place.get('vicinity', 'Address not available'),
                        'place_id': place.get('place_id', ''),
                        'rating': place.get('rating', 'N/A'),
                        'user_ratings_total': place.get('user_ratings_total', 0),
                        'operational_status': place.get('business_status', 'UNKNOWN')
                    })

                # Check if there are more results
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break

            except requests.exceptions.RequestException as e:
                print(f"Error fetching {type_label}: {e}")
                break

        return places

    def fetch_all_shelters(self) -> List[Dict]:
        """
        Fetch all shelter types (schools, police stations, fire stations).

        Returns:
            List of all shelter dictionaries
        """
        print(f"Searching for shelters around {self.location} within {self.radius}m radius...\n")

        for type_label, place_type in self.PLACE_TYPES.items():
            print(f"Fetching {type_label}...")
            places = self.fetch_places(place_type, type_label)
            self.all_shelters.extend(places)
            print(f"Total {type_label} found: {len(places)}\n")

        print(f"Total shelters found: {len(self.all_shelters)}")
        return self.all_shelters

    def export_to_excel(self, filename: str = None) -> str:
        """
        Export shelter data to Excel file.

        Args:
            filename: Output filename (default: shelters_YYYYMMDD_HHMMSS.xlsx)

        Returns:
            Path to the created Excel file
        """
        if not self.all_shelters:
            print("No shelter data to export. Run fetch_all_shelters() first.")
            return None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"shelters_{timestamp}.xlsx"

        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        # Create DataFrame
        df = pd.DataFrame(self.all_shelters)

        # Reorder columns for better readability
        column_order = ['name', 'type', 'latitude', 'longitude', 'address',
                       'rating', 'user_ratings_total', 'operational_status', 'place_id']
        df = df[column_order]

        # Create Excel writer with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write all shelters to main sheet
            df.to_excel(writer, sheet_name='All Shelters', index=False)

            # Create separate sheets for each type
            for type_label in self.PLACE_TYPES.keys():
                type_df = df[df['type'] == type_label]
                if not type_df.empty:
                    sheet_name = type_label.replace('_', ' ').title()
                    type_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"\nData exported successfully to: {filename}")
        print(f"Total records: {len(df)}")
        print(f"Breakdown:")
        for type_label in self.PLACE_TYPES.keys():
            count = len(df[df['type'] == type_label])
            print(f"  - {type_label}: {count}")

        return filename


def main():
    """Main function to run the shelter locator."""

    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key or set it as an environment variable.")
        sys.exit(1)

    # Get location from environment or use default (New York City)
    location = os.getenv('SEARCH_LOCATION', '40.7128,-74.0060')

    # Get radius from environment or use default (5000m)
    radius = int(os.getenv('SEARCH_RADIUS', '5000'))

    print("=" * 60)
    print("Crisis Shelter Locator")
    print("=" * 60)
    print(f"API Key: {'*' * 20}{api_key[-4:]}")
    print(f"Location: {location}")
    print(f"Radius: {radius}m")
    print("=" * 60 + "\n")

    # Create locator instance
    locator = ShelterLocator(api_key, location, radius)

    # Fetch all shelters
    locator.fetch_all_shelters()

    # Export to Excel
    if locator.all_shelters:
        locator.export_to_excel()
    else:
        print("\nNo shelters found. Please check your API key and search parameters.")
        sys.exit(1)


if __name__ == "__main__":
    main()
