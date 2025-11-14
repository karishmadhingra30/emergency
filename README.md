# Crisis Shelter Locator

A Python-based tool that uses Google Maps Places API to identify potential emergency shelter locations (schools, police stations, and fire stations) and export their coordinates to Excel for crisis management planning.

## Features

- Fetches locations of potential emergency shelters:
  - Schools
  - Police Stations
  - Fire Stations
- Exports data to Excel with multiple sheets for easy analysis
- Configurable search location and radius
- Includes location details: name, coordinates, address, ratings, and operational status
- Automatic pagination to retrieve all available results

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

Run the script:

```bash
python shelter_locator.py
```

The script will:
1. Connect to Google Maps Places API
2. Search for schools, police stations, and fire stations within the specified radius
3. Export results to an Excel file named `shelters_YYYYMMDD_HHMMSS.xlsx`

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

## Future Enhancements

Potential improvements for production use:
- Add more shelter types (hospitals, community centers, hotels)
- Implement geocoding for address-based searches
- Add capacity estimation based on building size
- Include accessibility information
- Real-time availability status integration
- Web interface for visualization
- Database storage instead of Excel
- Multi-location batch processing

## License

MIT License - feel free to use and modify for your crisis management needs.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
