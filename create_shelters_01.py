#!/usr/bin/env python3
"""
Create shelters_01.xlsx file with sample shelter data
"""

import pandas as pd

# Sample shelter data for Indian mountain regions
# Coordinates for Uttarakhand (Dehradun area)
sample_shelters = [
    # Schools in Dehradun area
    {
        'name': 'Doon Public School',
        'type': 'schools',
        'latitude': 30.3165,
        'longitude': 78.0322,
        'address': 'Dehradun, Uttarakhand',
        'rating': 4.5,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'Kendriya Vidyalaya No 1',
        'type': 'schools',
        'latitude': 30.3252,
        'longitude': 78.0425,
        'address': 'Clement Town, Dehradun, Uttarakhand',
        'rating': 4.2,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'Mussoorie Public School',
        'type': 'schools',
        'latitude': 30.4598,
        'longitude': 78.0644,
        'address': 'Mussoorie, Uttarakhand',
        'rating': 4.3,
        'operational_status': 'OPERATIONAL'
    },

    # Police Stations
    {
        'name': 'City Police Station',
        'type': 'police_stations',
        'latitude': 30.3255,
        'longitude': 78.0436,
        'address': 'Rajpur Road, Dehradun, Uttarakhand',
        'rating': 3.8,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'Cantt Police Station',
        'type': 'police_stations',
        'latitude': 30.3089,
        'longitude': 78.0488,
        'address': 'Dehradun Cantt, Uttarakhand',
        'rating': 3.9,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'Mussoorie Police Station',
        'type': 'police_stations',
        'latitude': 30.4552,
        'longitude': 78.0735,
        'address': 'Mall Road, Mussoorie, Uttarakhand',
        'rating': 4.0,
        'operational_status': 'OPERATIONAL'
    },

    # Fire Stations
    {
        'name': 'Central Fire Station',
        'type': 'fire_stations',
        'latitude': 30.3203,
        'longitude': 78.0377,
        'address': 'Clock Tower, Dehradun, Uttarakhand',
        'rating': 4.1,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'Clement Town Fire Station',
        'type': 'fire_stations',
        'latitude': 30.2656,
        'longitude': 78.0092,
        'address': 'Clement Town, Dehradun, Uttarakhand',
        'rating': 4.0,
        'operational_status': 'OPERATIONAL'
    },

    # Additional mountain area samples
    # Rishikesh area
    {
        'name': 'Rishikesh Police Station',
        'type': 'police_stations',
        'latitude': 30.0869,
        'longitude': 78.2676,
        'address': 'Rishikesh, Uttarakhand',
        'rating': 3.7,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'Government School Rishikesh',
        'type': 'schools',
        'latitude': 30.1033,
        'longitude': 78.2932,
        'address': 'Rishikesh, Uttarakhand',
        'rating': 4.0,
        'operational_status': 'OPERATIONAL'
    },

    # Haridwar area
    {
        'name': 'Haridwar Police Station',
        'type': 'police_stations',
        'latitude': 29.9457,
        'longitude': 78.1642,
        'address': 'Haridwar, Uttarakhand',
        'rating': 3.8,
        'operational_status': 'OPERATIONAL'
    },
    {
        'name': 'DAV Public School Haridwar',
        'type': 'schools',
        'latitude': 29.9525,
        'longitude': 78.1789,
        'address': 'Haridwar, Uttarakhand',
        'rating': 4.4,
        'operational_status': 'OPERATIONAL'
    },
]

# Create DataFrame
df = pd.DataFrame(sample_shelters)

# Save to Excel with specific filename
output_file = 'shelters_01.xlsx'
df.to_excel(output_file, index=False, sheet_name='All Shelters')

print(f"Created {output_file} with {len(df)} shelters")
