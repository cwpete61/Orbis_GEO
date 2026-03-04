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

    # Step 2: AI Analysis
    prompt = f"""You are a Local GEO (Generative Engine Optimization) expert.
Analyze the following search context for a Google Business Profile:
URL provided: {gbp_url}

Search Context:
{chr(10).join(results)}

Evaluate the "AI Readiness" of this local business. Consider:
1. Is the business name and category clear?
2. Does it have "AI-compatible" descriptions (full of entities, clear services)?
3. What is the sentiment of recent reviews/mentions?
4. How likely is an AI (like ChatGPT Local or Google SGE) to recommend this specific location?

Return a JSON object:
{{
    "business_name": "string",
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
