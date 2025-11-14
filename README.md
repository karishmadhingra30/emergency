# Crisis Shelter Locator & Offline Map Plotter

A comprehensive Python-based toolkit for emergency shelter management:
1. **Shelter Locator**: Fetches potential shelter locations using Google Maps Places API
2. **Offline Map Plotter**: Visualizes coordinates from Excel files on interactive offline-capable maps

## Features

### Shelter Locator
- Fetches locations of potential emergency shelters:
  - Schools
  - Police Stations
  - Fire Stations
- Exports data to Excel with multiple sheets for easy analysis
- Configurable search location and radius
- Includes location details: name, coordinates, address, ratings, and operational status
- Automatic pagination to retrieve all available results

### Offline Map Plotter (NEW)
- **Read Excel files** with latitude/longitude coordinates
- **Generate interactive HTML maps** using Leaflet.js and OpenStreetMap
- **Works offline** after initial map tile load (or with local tile server)
- **Color-coded markers** by category/type
- **Interactive popups** with detailed location information
- **Auto-zoom** to fit all markers
- **No API key required** for viewing maps

## Prerequisites

- Python 3.7 or higher
- Google Maps API Key with Places API enabled

## Getting a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Places API** for your project
4. Go to **Credentials** and create an API key
5. (Optional but recommended) Restrict your API key to only the Places API

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd emergency
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your Google Maps API key:
   ```
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   SEARCH_LOCATION=40.7128,-74.0060
   SEARCH_RADIUS=5000
   ```

## Configuration

Edit the `.env` file to customize your search:

- **GOOGLE_MAPS_API_KEY**: Your Google Maps API key (required)
- **SEARCH_LOCATION**: Center point for search in `latitude,longitude` format
  - Default: `40.7128,-74.0060` (New York City)
- **SEARCH_RADIUS**: Search radius in meters (default: 5000m = 5km)
  - Maximum recommended: 50000 (50km)

### Common Location Coordinates

- New York City: `40.7128,-74.0060`
- Los Angeles: `34.0522,-118.2437`
- Chicago: `41.8781,-87.6298`
- Houston: `29.7604,-95.3698`
- Phoenix: `33.4484,-112.0740`
- Philadelphia: `39.9526,-75.1652`

## Usage

### Shelter Locator

Run the shelter locator script:

```bash
python shelter_locator.py
```

The script will:
1. Connect to Google Maps Places API
2. Search for schools, police stations, and fire stations within the specified radius
3. Export results to an Excel file named `shelters_YYYYMMDD_HHMMSS.xlsx`

### Offline Map Plotter

Generate an interactive map from your Excel file:

```bash
python offline_map_plotter.py your_file.xlsx
```

**Basic Examples:**
```bash
# Plot data from Excel file (auto-detects lat/lon columns)
python offline_map_plotter.py shelters_20241114.xlsx

# Specify custom output filename
python offline_map_plotter.py shelters.xlsx --output my_map.html

# Specify custom column names
python offline_map_plotter.py data.xlsx --lat Latitude --lon Longitude --name Location

# Specify sheet name and add custom title
python offline_map_plotter.py data.xlsx --sheet "All Shelters" --title "Emergency Shelters Map"
```

**Command Line Options:**
- `--sheet <name>` - Sheet name to read (default: first sheet)
- `--lat <column>` - Latitude column name (default: 'latitude')
- `--lon <column>` - Longitude column name (default: 'longitude')
- `--name <column>` - Name/title column (default: 'name')
- `--type <column>` - Type/category column for color coding (default: 'type')
- `--output <file>` - Output HTML file name (default: 'offline_map.html')
- `--title <title>` - Map title (default: 'Location Map')

**Output:**
- Creates an HTML file with an interactive map
- Open the HTML file in any web browser (Chrome, Firefox, Safari, etc.)
- Works offline after initial tile load (tiles are cached by browser)

## Output Format

The Excel file contains multiple sheets:

1. **All Shelters**: Combined list of all locations
2. **Schools**: Only school locations
3. **Police Stations**: Only police station locations
4. **Fire Stations**: Only fire station locations

### Data Columns

- **name**: Name of the facility
- **type**: Type of shelter (schools/police_stations/fire_stations)
- **latitude**: Latitude coordinate
- **longitude**: Longitude coordinate
- **address**: Street address or vicinity
- **rating**: Google Maps rating (if available)
- **user_ratings_total**: Number of user ratings
- **operational_status**: Current operational status
- **place_id**: Google Places unique identifier

## Example Output

```
============================================================
Crisis Shelter Locator
============================================================
API Key: ********************AbCd
Location: 40.7128,-74.0060
Radius: 5000m
============================================================

Searching for shelters around 40.7128,-74.0060 within 5000m radius...

Fetching schools...
Found 20 schools in this batch
Total schools found: 20

Fetching police_stations...
Found 5 police_stations in this batch
Total police_stations found: 5

Fetching fire_stations...
Found 8 fire_stations in this batch
Total fire_stations found: 8

Total shelters found: 33

Data exported successfully to: shelters_20241114_123045.xlsx
Total records: 33
Breakdown:
  - schools: 20
  - police_stations: 5
  - fire_stations: 8
```

## API Usage Notes

- The Google Places API has usage limits and may incur costs
- The free tier includes $200 monthly credit (as of 2024)
- Nearby Search requests cost approximately $32 per 1000 requests
- Each search can return up to 60 results (3 pages of 20)
- Monitor your usage in the Google Cloud Console

## Troubleshooting

### "REQUEST_DENIED" Error

- Verify your API key is correct in `.env`
- Ensure Places API is enabled in Google Cloud Console
- Check if your API key has proper restrictions

### No Results Found

- Verify the location coordinates are correct
- Try increasing the search radius
- Check if the location has the types of facilities you're searching for

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Making Maps Fully Offline

By default, the offline map plotter uses OpenStreetMap tiles from the internet. The map will work offline **after** you've loaded it once (tiles are cached by your browser), but for **completely offline** use without any internet connection, you have several options:

### Option 1: Save Complete Web Page (Easiest)
1. Open the generated HTML map in your browser
2. Pan and zoom around the area to load tiles
3. Use your browser's "Save Page As" → "Webpage, Complete" to save all resources
4. The saved page will work offline with the cached tiles

### Option 2: Download Leaflet.js for Offline Use
The HTML file currently loads Leaflet from a CDN. To make it fully offline:

1. Download Leaflet.js and CSS:
```bash
mkdir -p offline_resources
cd offline_resources
wget https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
wget https://unpkg.com/leaflet@1.9.4/dist/leaflet.js
wget https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png
wget https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png
```

2. Modify the HTML file to reference local files instead of CDN links

### Option 3: Set Up Local Tile Server (Advanced)
For true offline mapping with full pan/zoom capabilities:

1. **Download map tiles** for your area using tools like:
   - [TileMill](https://tilemill-project.github.io/tilemill/)
   - [MapTiler](https://www.maptiler.com/)
   - Manual download with scripts

2. **Set up a simple tile server**:
```bash
# Example using Python's HTTP server
python -m http.server 8080
```

3. Place tiles in the correct directory structure: `tiles/{z}/{x}/{y}.png`

4. Run the map plotter with local tiles enabled (modify the script or use custom tile URL)

### Option 4: Use Static Map Images
If you don't need interactivity, you can generate static map images that are completely offline. Let me know if you need this functionality!

## Future Enhancements

Potential improvements for production use:
- Add more shelter types (hospitals, community centers, hotels)
- Implement geocoding for address-based searches
- Add capacity estimation based on building size
- Include accessibility information
- Real-time availability status integration
- Clustering for large datasets
- Heatmap visualization
- Distance/routing calculations between shelters
- Export to KML/GeoJSON formats
- Database storage instead of Excel
- Multi-location batch processing
- Mobile-responsive map interface

## License

MIT License - feel free to use and modify for your crisis management needs.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
