import requests
import json
import re
from urllib.parse import unquote

def scrape_address_and_get_osm(short_url):
    print(f"Resolving shortened URL: {short_url}")
    
    # 1. Expand Google Maps URL
    try:
        session = requests.Session()
        res = session.head(short_url, allow_redirects=True, timeout=10)
        final_url = unquote(res.url)
        print(f"Expanded URL:\n{final_url}\n")
    except Exception as e:
        print(f"Failed to expand URL: {e}")
        return

    # 2. Extract Coordinates from the Expanded URL
    # Format usually looks like: /@40.5401089,-75.4981855,15z
    coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', final_url)
    
    if coord_match:
        lat = coord_match.group(1)
        lon = coord_match.group(2)
        print(f"Direct Coordinate Match from URL! Lat: {lat}, Lon: {lon}")
        
        # We can then reverse geocode this in OSM to get the canonical structure
        print("\nReverse Geocoding Open Street Maps to get canonical address structure...")
        osm_url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'jsonv2'
        }
        headers = {'User-Agent': 'OrbisGEO-SEO-Test/1.0 (test@orbislocal.com)'}
        try:
            osm_res = requests.get(osm_url, params=params, headers=headers)
            print(json.dumps(osm_res.json(), indent=2))
        except Exception as e:
            print(f"OSM Reverse Geocode failed: {e}")
            
    else:
        print("No coordinates found in the URL. Printing raw URL for debugging:")
        print(final_url)

if __name__ == "__main__":
    test_url = "https://maps.app.goo.gl/EEKjPP9oKbUENTkR8"
    scrape_address_and_get_osm(test_url)
