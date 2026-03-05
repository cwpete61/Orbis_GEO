import sys
import json
import os
import re
from datetime import datetime

try:
    from duckduckgo_search import DDGS
    import openai
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print(json.dumps({"error": "Missing dependencies. Run: pip install duckduckgo_search openai python-dotenv"}))
    sys.exit(1)

def load_outscraper_maps():
    import glob
    import os
    import json
    # Outscraper webhook saves files as outscraper_maps_taskId.json
    latest_file = max(glob.glob('outscraper_maps_*.json'), key=os.path.getctime, default="test_outscraper_maps.json")
    if not os.path.exists(latest_file):
        return None
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
        return None
    except:
        return None

def analyze_gbp(gbp_url):
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
        search_query = f"Google Business Profile details for {gbp_url}"
    
    results = []
    try:
        with DDGS() as ddgs:
            # We search for the profile to see what the "public internet" knows about it
            # (which is what AI crawlers see)
            search_results = list(ddgs.text(search_query, max_results=5))
            results = [f"Title: {r['title']}\nSnippet: {r['body']}" for r in search_results]
    except Exception as e:
        results = [f"Search failed: {str(e)}"]

    import requests

    # Step 1.5: OSM Entity Verification 
    osm_data_str = "No OSM data retrieved."
    try:
        # Try to extract a clean business name from a standard maps URL
        possible_name = search_query
        if "place/" in gbp_url:
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
    outscraper_data = load_outscraper_maps()
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

Return a JSON object:
{{
    "business_name": "string",
    "osm_verification_confidence": 0-100,
    "overall_local_score": 0-100,
    "status": "Excellent|Good|Fair|Poor",
    "insights": [
        {{ "title": "string", "score": 0-100, "details": "string" }}
    ],
    "findings": [
        {{ "severity": "critical|high|medium|low", "title": "string", "description": "string", "impact": "string", "fix_example": "string" }}
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

    result = analyze_gbp(url)
    print(json.dumps(result, indent=2))
