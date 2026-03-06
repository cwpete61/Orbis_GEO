import sys
import json
import os
import re
from datetime import datetime

try:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    import openai
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install ddgs openai python-dotenv"}))
    sys.exit(1)

def load_outscraper_maps(gbp_url=""):
    import glob
    import os
    import json
    # Outscraper webhook saves files as outscraper_maps_taskId.json
    latest_file = max(glob.glob('outscraper_maps_*.json'), key=os.path.getctime, default="test_outscraper_maps.json")
    if os.path.exists(latest_file):
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                item = data[0]
                if isinstance(item, list) and len(item) > 0:
                    item = item[0]
                if isinstance(item, dict):
                    return {
                        "rating": item.get('rating'),
                        "reviews_data": item.get('reviews_data', []),
                        "reviews": item.get('reviews'), # count
                        "attributes": item.get('about', {})
                    }
        except:
            pass
            
    # Fallback to direct synchronous fetch using Outscraper Python SDK
    import sys
    api_key = os.getenv("OUTSCRAPER_API_KEY")
    if api_key and gbp_url:
        try:
            from outscraper import ApiClient
            client = ApiClient(api_key=api_key)
            print(f"[gbp_analyzer] Fetching Outscraper maps data synchronously for {gbp_url}...", file=sys.stderr)
            results = client.maps_search([gbp_url], limit=1)
            if results and len(results) > 0:
                item = results[0]
                if isinstance(item, list) and len(item) > 0:
                    item = item[0]
                if isinstance(item, dict):
                    return {
                        "rating": item.get('rating'),
                        "reviews_data": item.get('reviews_data', []),
                        "reviews": item.get('reviews'), # count
                        "attributes": item.get('about', {})
                    }
        except Exception as e:
            print(f"[gbp_analyzer] Outscraper SDK error: {e}", file=sys.stderr)
            
    return None

def analyze_gbp(gbp_url, brand_name=""):
    """Analyze a Google Business Profile for GEO-SEO optimization."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY not found in environment"}

    # Initialize OpenAI
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Step 1: Extract business intent from URL or search
    # If it's a URL, we try to guess the business name or search for the URL itself
    search_query = gbp_url
    if "maps.app.goo.gl" in gbp_url or "google.com/maps" in gbp_url:
        if brand_name:
            search_query = f"{brand_name} Google Business Profile reviews rating"
        else:
            search_query = f"Google Business Profile details for {gbp_url}"
    
    results = []
    
    import time
    import random
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(1.0, 3.0))
            with DDGS() as ddgs:
                search_results = list(ddgs.text(search_query, max_results=5))
                results = [f"Title: {r['title']}\nSnippet: {r['body']}" for r in search_results]
            if results:
                break
        except Exception as e:
            if attempt == max_retries - 1:
                results = [f"Search failed after {max_retries} attempts: {str(e)}"]
            else:
                time.sleep(random.uniform(2.0, 5.0))
                
    print(f"[gbp_analyzer] Found {len(results)} search snippets for query: {search_query}", file=sys.stderr)

    import requests

    # Step 1.5: OSM Entity Verification 
    osm_data_str = "No OSM data retrieved."
    try:
        # Try to extract a clean business name from a standard maps URL
        possible_name = brand_name if brand_name else search_query
        if not brand_name and "place/" in gbp_url:
            parts = gbp_url.split("place/")[1].split("/")
            if len(parts) > 0:
                possible_name = parts[0].replace("+", " ")
        
        # We query the OSM Nominatim API searching for the query.
        osm_url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(possible_name)}&format=jsonv2&addressdetails=1&extratags=1&limit=3"
        headers = {'User-Agent': 'OrbisGEO-SEO/1.0 (Integration Test)'}
        osm_response = requests.get(osm_url, headers=headers, timeout=5)
        if osm_response.status_code == 200:
            osm_results = osm_response.json()
            osm_lines = []
            for r in osm_results:
                name = r.get('name', 'N/A')
                display = r.get('display_name', 'N/A')
                tags = r.get('extratags', {})
                website = tags.get('website', tags.get('contact:website', 'N/A'))
                wikidata = tags.get('wikidata', tags.get('brand:wikidata', 'N/A'))
                osm_lines.append(f"- Name: {name} | Address: {display} | Website: {website} | Wikidata: {wikidata}")
            if osm_lines:
                osm_data_str = "\n".join(osm_lines)
    except Exception as e:
        osm_data_str = f"OSM Search failed: {str(e)}"

    # Step 2: AI Analysis
    outscraper_data = load_outscraper_maps(gbp_url)
    outscraper_str = "No verified Outscraper data available."
    if outscraper_data:
        outscraper_str = f"- Rating: {outscraper_data.get('rating')}\n- Reviews count: {outscraper_data.get('reviews')}\n- Attributes: {json.dumps(outscraper_data.get('attributes'))}"

    prompt = f"""You are a Local GEO (Generative Engine Optimization) expert.
Analyze the following search context for a Google Business Profile:
URL provided: {gbp_url}

Search Context:
{chr(10).join(results)}

Open Street Maps (OSM) Entity Cross-Validation Data:
{osm_data_str}

Outscraper Verified Data:
{outscraper_str}

Evaluate the "AI Readiness" of this local business. Consider:
1. Is the business name and category clear?
2. Does it have "AI-compatible" descriptions (full of entities, clear services)?
3. What is the sentiment of recent reviews/mentions?
4. Entity Verification: Cross-reference the GBP Search Context against the OSM Entity Data. If the canonical OSM data (address, website, wikidata) does not match the GBP results, it indicates an entity mismatch.

IMPORTANT: Do not output placeholder values like "string". You MUST extract or infer the actual business name.
If you cannot determine the business name, use "Unknown Business".

SCORING GUIDANCE for `overall_local_score`:
- 80-100: Excellent business with clear search presence and multiple entity signals.
- 50-79: Average to good business with decent search presence. Missing OSM data is common, do not heavily penalize if search context confirms the business exists!
- 30-49: Poor presence, few mentions, and no entity data.
- 0-29: Ghost entity. Completely missing from search and no data anywhere.

Return a JSON object:
{{
    "business_name": "<the actual name of the business>",
    "osm_verification_confidence": 0-100,
    "overall_local_score": 0-100,
    "status": "Excellent|Good|Fair|Poor",
    "insights": [
        {{ "title": "<specific descriptive title>", "score": 0-100, "details": "<detailed explanation>" }}
    ],
    "findings": [
        {{ "severity": "critical|high|medium|low", "title": "<finding title>", "description": "<description>", "impact": "<impact>", "fix_example": "<how to fix>" }}
    ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        analysis["audit_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        analysis["gbp_url"] = gbp_url
        return analysis

    except Exception as e:
        return {"error": f"AI Analysis failed: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python gbp_analyzer.py <gbp_url>"}))
        sys.exit(1)

    url = sys.argv[1]
    brand = sys.argv[2] if len(sys.argv) > 2 else ""
    # Simple check for empty or placeholder strings
    if not url or url.strip() == "" or url == "undefined":
        print(json.dumps({
            "business_name": "Not Provided",
            "overall_local_score": 0,
            "status": "N/A",
            "insights": [],
            "findings": [{"severity": "info", "title": "No GBP URL", "description": "No Google Business Profile was provided for analysis."}]
        }))
        sys.exit(0)

    result = analyze_gbp(url, brand)
    print(json.dumps(result, indent=2))
