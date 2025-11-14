#!/usr/bin/env python3
"""
Create sample Excel file with coordinates for testing the offline map plotter.
"""

import pandas as pd

# Sample data - various locations in New York City
sample_data = [
    {
        'name': 'Central Park',
        'type': 'Park',
        'latitude': 40.785091,
        'longitude': -73.968285,
        'address': 'Central Park, New York, NY',
        'notes': 'Large urban park'
    },
    {
        'name': 'Empire State Building',
        'type': 'Landmark',
        'latitude': 40.748817,
        'longitude': -73.985428,
        'address': '350 5th Ave, New York, NY 10118',
        'notes': 'Historic skyscraper'
    },
    {
        'name': 'Statue of Liberty',
        'type': 'Landmark',
        'latitude': 40.689247,
        'longitude': -74.044502,
        'address': 'Liberty Island, New York, NY',
        'notes': 'National monument'
    },
    {
        'name': 'Times Square',
        'type': 'Landmark',
        'latitude': 40.758896,
        'longitude': -73.985130,
        'address': 'Manhattan, NY 10036',
        'notes': 'Major commercial intersection'
    },
    {
        'name': 'Brooklyn Bridge',
        'type': 'Bridge',
        'latitude': 40.706086,
        'longitude': -73.996864,
        'address': 'Brooklyn Bridge, New York, NY',
        'notes': 'Iconic suspension bridge'
    },
    {
        'name': 'Grand Central Terminal',
        'type': 'Transportation',
        'latitude': 40.752726,
        'longitude': -73.977229,
        'address': '89 E 42nd St, New York, NY 10017',
        'notes': 'Historic train station'
    }
]

# Create DataFrame
df = pd.DataFrame(sample_data)

# Save to Excel
output_file = 'sample_locations.xlsx'
df.to_excel(output_file, index=False, sheet_name='Locations')

print(f"✓ Created sample Excel file: {output_file}")
print(f"✓ Contains {len(df)} sample locations")
print(f"\nColumns: {', '.join(df.columns)}")
print(f"\nYou can now test the offline map plotter with:")
print(f"  python offline_map_plotter.py {output_file}")
