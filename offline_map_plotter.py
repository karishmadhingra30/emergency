#!/usr/bin/env python3
"""
Offline Map Plotter
Reads latitude/longitude data from Excel files and generates an interactive
HTML map using Leaflet.js and OpenStreetMap tiles.
"""

import os
import sys
import pandas as pd
from typing import List, Dict, Optional
import json


class OfflineMapPlotter:
    """Generates offline-capable interactive maps from Excel coordinate data."""

    def __init__(self, excel_file: str):
        """
        Initialize the OfflineMapPlotter.

        Args:
            excel_file: Path to Excel file containing latitude and longitude columns
        """
        self.excel_file = excel_file
        self.data = None
        self.markers = []

    def read_excel(self, sheet_name: Optional[str] = None,
                   lat_col: str = 'latitude',
                   lon_col: str = 'longitude') -> pd.DataFrame:
        """
        Read Excel file and extract coordinate data.

        Args:
            sheet_name: Name of sheet to read (default: first sheet)
            lat_col: Name of latitude column (default: 'latitude')
            lon_col: Name of longitude column (default: 'longitude')

        Returns:
            DataFrame with coordinate data
        """
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(self.excel_file)

            print(f"Read {len(df)} rows from Excel file")
            print(f"Columns found: {', '.join(df.columns)}")

            # Check if lat/lon columns exist
            if lat_col not in df.columns or lon_col not in df.columns:
                print(f"\nError: Could not find '{lat_col}' and/or '{lon_col}' columns")
                print(f"Available columns: {', '.join(df.columns)}")
                print("\nTrying to auto-detect coordinate columns...")

                # Try common variations
                lat_variations = ['lat', 'latitude', 'Latitude', 'LAT', 'LATITUDE']
                lon_variations = ['lon', 'long', 'longitude', 'Longitude', 'LON', 'LONGITUDE', 'lng']

                lat_col = next((col for col in df.columns if col in lat_variations), None)
                lon_col = next((col for col in df.columns if col in lon_variations), None)

                if not lat_col or not lon_col:
                    print("Could not auto-detect coordinate columns. Please specify column names.")
                    return None

                print(f"Auto-detected: {lat_col}, {lon_col}")

            # Filter out rows with missing coordinates
            df_clean = df.dropna(subset=[lat_col, lon_col])

            if len(df_clean) < len(df):
                print(f"Removed {len(df) - len(df_clean)} rows with missing coordinates")

            # Validate coordinate ranges
            invalid_coords = df_clean[
                (df_clean[lat_col] < -90) | (df_clean[lat_col] > 90) |
                (df_clean[lon_col] < -180) | (df_clean[lon_col] > 180)
            ]

            if len(invalid_coords) > 0:
                print(f"Warning: Found {len(invalid_coords)} rows with invalid coordinates (out of range)")
                df_clean = df_clean[
                    (df_clean[lat_col] >= -90) & (df_clean[lat_col] <= 90) &
                    (df_clean[lon_col] >= -180) & (df_clean[lon_col] <= 180)
                ]

            print(f"Valid coordinates: {len(df_clean)}")

            self.data = df_clean
            self.lat_col = lat_col
            self.lon_col = lon_col

            return df_clean

        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None

    def prepare_markers(self, name_col: Optional[str] = 'name',
                       type_col: Optional[str] = 'type',
                       additional_cols: Optional[List[str]] = None) -> List[Dict]:
        """
        Prepare marker data for map visualization.

        Args:
            name_col: Column to use for marker name/title
            type_col: Column to use for marker type/category
            additional_cols: Additional columns to include in popup

        Returns:
            List of marker dictionaries
        """
        if self.data is None:
            print("Error: No data loaded. Run read_excel() first.")
            return []

        markers = []

        for idx, row in self.data.iterrows():
            marker = {
                'lat': float(row[self.lat_col]),
                'lon': float(row[self.lon_col]),
                'name': str(row[name_col]) if name_col in self.data.columns else f"Location {idx + 1}",
                'type': str(row[type_col]) if type_col in self.data.columns else "Unknown"
            }

            # Add additional info for popup
            popup_info = {}
            if additional_cols:
                for col in additional_cols:
                    if col in self.data.columns:
                        popup_info[col] = str(row[col])
            else:
                # Include all columns except coordinates
                for col in self.data.columns:
                    if col not in [self.lat_col, self.lon_col]:
                        popup_info[col] = str(row[col])

            marker['info'] = popup_info
            markers.append(marker)

        self.markers = markers
        print(f"Prepared {len(markers)} markers for map")
        return markers

    def generate_html_map(self, output_file: str = "offline_map.html",
                         map_title: str = "Location Map",
                         use_offline_tiles: bool = False) -> str:
        """
        Generate interactive HTML map with markers.

        Args:
            output_file: Name of output HTML file
            map_title: Title for the map page
            use_offline_tiles: If True, use local tile server (requires setup)

        Returns:
            Path to generated HTML file
        """
        if not self.markers:
            print("Error: No markers prepared. Run prepare_markers() first.")
            return None

        # Calculate center point (average of all coordinates)
        avg_lat = sum(m['lat'] for m in self.markers) / len(self.markers)
        avg_lon = sum(m['lon'] for m in self.markers) / len(self.markers)

        # Determine appropriate zoom level based on coordinate spread
        lat_range = max(m['lat'] for m in self.markers) - min(m['lat'] for m in self.markers)
        lon_range = max(m['lon'] for m in self.markers) - min(m['lon'] for m in self.markers)
        max_range = max(lat_range, lon_range)

        if max_range > 10:
            zoom = 6
        elif max_range > 5:
            zoom = 8
        elif max_range > 1:
            zoom = 10
        elif max_range > 0.1:
            zoom = 12
        else:
            zoom = 14

        # Tile server URL (can be changed for offline use)
        if use_offline_tiles:
            tile_url = "http://localhost:8080/tile/{z}/{x}/{y}.png"
            attribution = "Local tiles"
        else:
            # Using OpenStreetMap tiles (requires internet on first load, then caches)
            tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

        # Prepare markers data as JSON
        markers_json = json.dumps(self.markers, indent=2)

        # Color coding for different types
        type_colors = {}
        unique_types = list(set(m['type'] for m in self.markers))
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'darkblue', 'darkgreen']
        for i, type_name in enumerate(unique_types):
            type_colors[type_name] = colors[i % len(colors)]

        type_colors_json = json.dumps(type_colors)

        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{map_title}</title>

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossorigin=""/>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
            crossorigin=""></script>

    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}

        #map {{
            position: absolute;
            top: 60px;
            bottom: 0;
            width: 100%;
        }}

        .header {{
            position: fixed;
            top: 0;
            width: 100%;
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }}

        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}

        .stats {{
            position: absolute;
            top: 70px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 250px;
        }}

        .stats h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}

        .legend {{
            line-height: 18px;
            color: #555;
        }}

        .legend i {{
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            border-radius: 50%;
        }}

        .popup-content {{
            font-size: 14px;
        }}

        .popup-content h4 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}

        .popup-content table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .popup-content td {{
            padding: 3px 5px;
            border-bottom: 1px solid #eee;
        }}

        .popup-content td:first-child {{
            font-weight: bold;
            color: #555;
            width: 40%;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{map_title}</h1>
    </div>

    <div class="stats">
        <h3>Statistics</h3>
        <p><strong>Total Locations:</strong> <span id="total-count">{len(self.markers)}</span></p>
        <div class="legend" id="legend"></div>
    </div>

    <div id="map"></div>

    <script>
        // Initialize map
        const map = L.map('map').setView([{avg_lat}, {avg_lon}], {zoom});

        // Add tile layer
        L.tileLayer('{tile_url}', {{
            maxZoom: 19,
            attribution: '{attribution}'
        }}).addTo(map);

        // Marker data
        const markers = {markers_json};

        // Type colors
        const typeColors = {type_colors_json};

        // Create custom icon function
        function getIcon(type) {{
            const color = typeColors[type] || 'gray';
            return L.icon({{
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${{color}}.png`,
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            }});
        }}

        // Add markers to map
        const markerLayer = L.layerGroup().addTo(map);

        markers.forEach(marker => {{
            // Create popup content
            let popupContent = `<div class="popup-content">
                <h4>${{marker.name}}</h4>
                <table>
                    <tr><td>Type</td><td>${{marker.type}}</td></tr>
                    <tr><td>Latitude</td><td>${{marker.lat.toFixed(6)}}</td></tr>
                    <tr><td>Longitude</td><td>${{marker.lon.toFixed(6)}}</td></tr>`;

            // Add additional info
            for (const [key, value] of Object.entries(marker.info)) {{
                if (key !== 'name' && key !== 'type') {{
                    popupContent += `<tr><td>${{key}}</td><td>${{value}}</td></tr>`;
                }}
            }}

            popupContent += `</table></div>`;

            // Create marker
            const markerIcon = getIcon(marker.type);
            const leafletMarker = L.marker([marker.lat, marker.lon], {{ icon: markerIcon }})
                .bindPopup(popupContent)
                .addTo(markerLayer);
        }});

        // Fit map to show all markers
        if (markers.length > 0) {{
            const group = new L.featureGroup(markerLayer.getLayers());
            map.fitBounds(group.getBounds().pad(0.1));
        }}

        // Generate legend
        const legend = document.getElementById('legend');
        const typeCounts = {{}};

        markers.forEach(marker => {{
            typeCounts[marker.type] = (typeCounts[marker.type] || 0) + 1;
        }});

        let legendHTML = '<h4 style="margin: 10px 0 5px 0;">Categories</h4>';
        for (const [type, count] of Object.entries(typeCounts)) {{
            const color = typeColors[type] || 'gray';
            legendHTML += `<div><i style="background: ${{color}}"></i> ${{type}} (${{count}})</div>`;
        }}

        legend.innerHTML = legendHTML;

        console.log(`Loaded ${{markers.length}} markers on the map`);
    </script>
</body>
</html>"""

        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n✓ Map generated successfully: {output_file}")
        print(f"✓ Total markers: {len(self.markers)}")
        print(f"✓ Center: ({avg_lat:.6f}, {avg_lon:.6f})")
        print(f"✓ Zoom level: {zoom}")
        print(f"\nOpen '{output_file}' in your web browser to view the map.")

        if not use_offline_tiles:
            print("\nNote: Map tiles are loaded from OpenStreetMap servers.")
            print("For fully offline use, see instructions for setting up local tile server.")

        return output_file


def main():
    """Main function to run the offline map plotter."""

    if len(sys.argv) < 2:
        print("Offline Map Plotter")
        print("=" * 60)
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <excel_file> [options]")
        print("\nOptions:")
        print("  --sheet <name>        Sheet name to read (default: first sheet)")
        print("  --lat <column>        Latitude column name (default: 'latitude')")
        print("  --lon <column>        Longitude column name (default: 'longitude')")
        print("  --name <column>       Name/title column (default: 'name')")
        print("  --type <column>       Type/category column (default: 'type')")
        print("  --output <file>       Output HTML file (default: 'offline_map.html')")
        print("  --title <title>       Map title (default: 'Location Map')")
        print("\nExample:")
        print(f"  python {sys.argv[0]} shelters.xlsx --output my_map.html")
        print(f"  python {sys.argv[0]} data.xlsx --lat Latitude --lon Longitude")
        sys.exit(1)

    excel_file = sys.argv[1]

    if not os.path.exists(excel_file):
        print(f"Error: File '{excel_file}' not found")
        sys.exit(1)

    # Parse command line arguments
    args = {
        'sheet_name': None,
        'lat_col': 'latitude',
        'lon_col': 'longitude',
        'name_col': 'name',
        'type_col': 'type',
        'output_file': 'offline_map.html',
        'map_title': 'Location Map'
    }

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--sheet' and i + 1 < len(sys.argv):
            args['sheet_name'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--lat' and i + 1 < len(sys.argv):
            args['lat_col'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--lon' and i + 1 < len(sys.argv):
            args['lon_col'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--name' and i + 1 < len(sys.argv):
            args['name_col'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--type' and i + 1 < len(sys.argv):
            args['type_col'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            args['output_file'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--title' and i + 1 < len(sys.argv):
            args['map_title'] = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    print("=" * 60)
    print("Offline Map Plotter")
    print("=" * 60)
    print(f"Input file: {excel_file}")
    print(f"Output file: {args['output_file']}")
    print("=" * 60 + "\n")

    # Create plotter instance
    plotter = OfflineMapPlotter(excel_file)

    # Read Excel data
    df = plotter.read_excel(
        sheet_name=args['sheet_name'],
        lat_col=args['lat_col'],
        lon_col=args['lon_col']
    )

    if df is None or len(df) == 0:
        print("\nNo valid data found. Exiting.")
        sys.exit(1)

    # Prepare markers
    plotter.prepare_markers(
        name_col=args['name_col'],
        type_col=args['type_col']
    )

    # Generate HTML map
    plotter.generate_html_map(
        output_file=args['output_file'],
        map_title=args['map_title']
    )


if __name__ == "__main__":
    main()
