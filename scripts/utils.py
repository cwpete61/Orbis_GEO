import math
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def get_distance_py(lat1, lon1, lat2, lon2):
    """Calculate Haversine distance in km."""
    R = 6371 # km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

import subprocess

def geocode_business(brand_name, gbp_url):
    """
    Find coordinates based on brand/URL context.
    Pipeline:
    1. Direct brand search via Open Street Maps (Nominatim API).
    2. If Google Maps URL, use Puppeteer to scrape the exact physical address.
    3. Fallback to OpenAI if all else fails.
    """
    import requests
    
    # Stage 0: Check Outscraper Verification Data
    import glob
    import os
    import json
    try:
        latest_file = max(glob.glob('outscraper_maps_*.json'), key=os.path.getctime, default="")
        if latest_file and os.path.exists(latest_file):
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                if isinstance(item, list) and len(item) > 0:
                    item = item[0]
                if isinstance(item, dict) and 'latitude' in item and 'longitude' in item:
                    print(f"[geocode] Using verified Outscraper coordinate data for: {brand_name}", file=sys.stderr)
                    return {
                        "lat": float(item['latitude']),
                        "lng": float(item['longitude']),
                        "address": item.get('full_address', item.get('city', f"Location for {brand_name}"))
                    }
    except Exception as e:
        print(f"[geocode] Outscraper fallback failed: {e}", file=sys.stderr)
        
    # Stage 1: OSM Nominatim Direct Brand Search
    try:
        print(f"[geocode] Querying OSM for precise coordinates of brand: {brand_name}", file=sys.stderr)
        osm_url = "https://nominatim.openstreetmap.org/search"
        res = requests.get(osm_url, params={'q': brand_name, 'format': 'json', 'limit': 1}, 
                           headers={'User-Agent': 'OrbisGEO-SEO/1.0'}, timeout=10)
        data = res.json()
        if data:
            address_str = data[0].get('display_name', f"Location for {brand_name}")
            return {
                "lat": float(data[0]['lat']),
                "lng": float(data[0]['lon']),
                "address": address_str
            }
    except Exception as e:
        print(f"[geocode] Direct OSM Search Failed: {e}", file=sys.stderr)

    # Stage 2: Puppeteer Google Maps Scrape
    address_str = ""
    if "maps.app.goo.gl" in gbp_url or "google.com/maps" in gbp_url:
        print(f"[geocode] Attempting headless extraction of exact address from: {gbp_url}", file=sys.stderr)
        
        js_code = f"""
const puppeteer = require('puppeteer');
(async () => {{
    try {{
        const browser = await puppeteer.launch({{ headless: "new", args: ['--no-sandbox'] }});
        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
        await page.goto('{gbp_url}', {{ waitUntil: 'networkidle2', timeout: 15000 }});
        const address = await page.evaluate(() => {{
            const btn = document.querySelector('button[data-item-id="address"]');
            if (btn) return btn.getAttribute('aria-label') || btn.innerText;
            const divs = Array.from(document.querySelectorAll('div'));
            for (let d of divs) {{
                if (d.innerText && d.innerText.match(/,\\s*[A-Z]{{2}}\\s*\\d{{5}}/)) return d.innerText;
            }}
            return "";
        }});
        console.log(address.replace('Address: ', '').trim());
        await browser.close();
    }} catch(e) {{
        console.log("");
    }}
}})();
"""
        import subprocess
        try:
            import os as _os
            scraper_path = _os.path.join("dashboard", "temp_scraper.js")
            with open(scraper_path, "w") as f:
                f.write(js_code)
            
            result = subprocess.run(["node", "temp_scraper.js"], cwd="dashboard", capture_output=True, text=True, timeout=20)
            
            if result.stdout.strip():
                address_str = result.stdout.strip()
                print(f"[geocode] Puppeteer successfully found exact address: {address_str}", file=sys.stderr)
            if _os.path.exists(scraper_path):
                _os.remove(scraper_path)
        except Exception as e:
            print(f"[geocode] Puppeteer scrape failed: {e}", file=sys.stderr)

    # Stage 3: OSM Nominatim Geocoding of scraped address
    if address_str:
        try:
            print(f"[geocode] Querying OSM for precise coordinates of: {address_str}", file=sys.stderr)
            osm_url = "https://nominatim.openstreetmap.org/search"
            clean_addr = address_str.split('\n')[0].strip()
            
            res = requests.get(osm_url, params={'q': clean_addr, 'format': 'json', 'limit': 1}, 
                               headers={'User-Agent': 'OrbisGEO-SEO/1.0'}, timeout=10)
            data = res.json()
            if data:
                return {
                    "lat": float(data[0]['lat']),
                    "lng": float(data[0]['lon']),
                    "address": address_str
                }
        except Exception as e:
            print(f"[geocode] OSM Failed: {e}", file=sys.stderr)

    # Stage 4: AI Fallback
    print(f"[geocode] Falling back to AI geocoding for {brand_name}...", file=sys.stderr)
    from openai import OpenAI
    import os, json
    
    website_text = ""
    if os.path.exists("test_fetch.json"):
        try:
            with open("test_fetch.json", "r", encoding="utf-8") as f:
                fetch_data = json.load(f)
                website_text = fetch_data.get("text_content", "")[:3000]
        except:
            pass

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    prompt = f"""You are a Geocoding expert. Given a business brand name and a Google Maps/GBP URL, 
find the EXACT latitude and longitude coordinates for this specific business location.

Brand: {brand_name}
GBP URL: {gbp_url}

Context from website scrape (may contain address):
{website_text}

IMPORTANT:
1. If the URL is a shortened 'maps.app.goo.gl' link, use your knowledge of Google Maps patterns to find the destination.
2. If no GBP URL is provided, carefully read the website context to find the physical address (e.g. city, street), then geocode it.
3. Return the coordinates for the SPECIFIC address associated with the brand and URL provided.
4. If you absolutely cannot determine the city or address, use the best generic location (e.g. center of the US or country) but set address to "Location undetermined". Do NOT hallucinate a fake street address like "123 Main Street".

Return ONLY a JSON object:
{{
    "lat": 0.0,
    "lng": 0.0,
    "address": "full address string"
}}
"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"lat": 34.0522, "lng": -118.2437, "address": "Default Location (Los Angeles)"}

def get_score_color_hex(score):
    """Return hex color based on score value."""
    # Note: These match the reportlab colors used in generate_pdf_report
    if score >= 80: return "#2ecc71" # SUCCESS
    if score >= 60: return "#3498db" # INFO
    if score >= 40: return "#f1c40f" # WARNING
    return "#e74c3c" # DANGER

def get_score_label(score):
    """Return label based on score value."""
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 55: return "Moderate"
    if score >= 40: return "Below Average"
    return "Needs Attention"
