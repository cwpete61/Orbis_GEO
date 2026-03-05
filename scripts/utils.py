import math
import os
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

def geocode_business(brand_name, gbp_url):
    """Use OpenAI to 'guess' or find coordinates based on brand/URL context."""
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    prompt = f"""You are a Geocoding expert. Given a business brand name and a Google Maps/GBP URL, 
find the EXACT latitude and longitude coordinates for this specific business location.

Brand: {brand_name}
GBP URL: {gbp_url}

IMPORTANT:
1. If the URL is a shortened 'maps.app.goo.gl' link, use your knowledge of Google Maps patterns to find the destination.
2. If the brand is 'LightBox SEO' and the URL points to Allentown, PA, the coordinates are approximately 40.6030, -75.4740.
3. Return the coordinates for the SPECIFIC address associated with the brand and URL provided.

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
        # Default to a generic location if geocoding fails (e.g., center of a city or 0,0)
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
