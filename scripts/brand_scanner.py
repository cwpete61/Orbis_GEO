#!/usr/bin/env python3
"""
Brand Mention Scanner — Checks brand presence across AI-cited platforms.

Uses DuckDuckGo search + OpenAI GPT to actively analyze brand presence
across YouTube, Reddit, Wikipedia, LinkedIn, and other platforms that
AI models rely on for entity recognition and citation decisions.

Based on Ahrefs December 2025 study of 75,000 brands:
- YouTube mentions: ~0.737 correlation (STRONGEST)
- Reddit mentions: High correlation
- Wikipedia presence: High correlation
- LinkedIn presence: Moderate correlation
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

try:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
except ImportError:
    print("ERROR: Run: pip install ddgs")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: Run: pip install openai")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: Run: pip install requests")
    sys.exit(1)

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not found. Check your .env file.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_domain(url: str) -> str:
    """Extract clean domain from a URL for search disambiguation."""
    if not url:
        return ""
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    domain = domain.replace("www.", "")
    return domain


def ddg_search(query: str, max_results: int = 6) -> list[str]:
    """Perform a DuckDuckGo search and return a list of snippet strings."""
    snippets = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "")
                body = r.get("body", "")
                href = r.get("href", "")
                snippets.append(f"[{title}] ({href}): {body}")
    except Exception as e:
        snippets.append(f"Search failed: {e}")
    return snippets


def validate_snippets(brand: str, snippets: list[str]) -> bool:
    """Check if any DDG snippets actually mention the brand name.
    Returns True if the brand appears meaningfully in at least one snippet."""
    if not snippets:
        return False
    brand_lower = brand.lower()
    for s in snippets:
        if "Search failed" in s:
            continue
        if brand_lower in s.lower():
            return True
    return False


def analyze_with_ai(brand: str, platform: str, snippets: list[str], criteria: str) -> dict:
    """Use OpenAI to analyze brand presence from search snippets."""
    snippet_text = "\n".join(snippets) if snippets else "No search results found."

    prompt = f"""You are a GEO (Generative Engine Optimization) analyst evaluating brand presence.

Brand: {brand}
Platform: {platform}

Search results found:
{snippet_text}

Evaluate the brand's presence on {platform} based on these search results.
{criteria}

Respond ONLY with a valid JSON object with this exact structure:
{{
  "score": <integer 0-100>,
  "has_presence": <true/false>,
  "key_findings": [<string>, <string>, <string>],
  "sentiment": "<positive|negative|neutral|mixed|unknown>",
  "summary": "<one sentence summary>"
}}"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "score": 10,
            "has_presence": False,
            "key_findings": [f"AI analysis failed: {e}"],
            "sentiment": "unknown",
            "summary": "Could not analyze this platform due to an API error."
        }


def check_youtube(brand: str, url: str = "") -> dict:
    """Check YouTube brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    
    # Search for channel specifically, but also standard videos
    snippets = ddg_search(f'"{brand}"{domain_term} youtube channel', max_results=3)
    snippets += ddg_search(f'site:youtube.com "{brand}"{domain_term}', max_results=3)
    
    # Check for general video mentions, requiring the brand name in quotes
    snippets += ddg_search(f'site:youtube.com "{brand}" review', max_results=4)

    criteria = """Score based on:
- 90-100: Verified official channel (youtube.com/@BrandName or /channel/) AND active highly relevant video mentions.
- 70-89: Brand clearly has videos (youtube.com/watch?v=...) OR channel, and is heavily reviewed/mentioned in 10+ videos.
- 50-69: Brand has some videos (youtube.com/watch?v=...) directly published by them, OR mentioned in 5-9 highly relevant videos.
- 30-49: No official channel found, mentioned in 1-4 videos by others.
- 10-29: Extremely rare 1-2 video mentions.
- 0-9: No YouTube presence at all.

CRITICAL INSTRUCTIONS FOR AI:
1. Examine the URLs in the search results closely.
2. If NO result URLs start with 'https://www.youtube.com/', then the brand DOES NOT have a highly relevant YouTube presence.
3. If they only have /watch?v= links but NO @channel links, they can still score up to 85 if the videos are clearly about their brand.
4. If there are NO search results containing the exact phrase for the brand, the score MUST be 0. Do not guess."""

    analysis = analyze_with_ai(brand, "YouTube", snippets, criteria)
    
    # Force a score of 0 if DDG found literally nothing or LLM hallucinated
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No YouTube presence detected."
    elif not validate_snippets(brand, snippets) and not any("youtube.com" in s for s in snippets):
        # No brand mention in snippets AND no youtube URLs — cap score
        analysis["score"] = min(analysis.get("score", 0), 10)
    elif analysis.get("score", 0) > 40 and not any("youtube.com" in s for s in snippets):
         # Downgrade if AI scored too high but no youtube url is in the snippets at all
         analysis["score"] = min(analysis.get("score", 0), 20)

    return {
        "platform": "YouTube",
        "correlation": 0.737,
        "weight": "25%",
        "score": analysis.get("score", 0),
        "has_channel": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.youtube.com/results?search_query={brand.replace(' ', '+')}",
        "recommendations": [
            "Create a YouTube channel if none exists",
            "Publish educational/tutorial content related to your niche",
            "Encourage customers to create review/demo videos",
            "Optimize video titles and descriptions with brand name",
        ]
    }


def check_reddit(brand: str, url: str = "") -> dict:
    """Check Reddit brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    
    snippets = ddg_search(f'"{brand}"{domain_term} site:reddit.com recommendations', max_results=6)
    snippets += ddg_search(f'"{brand}"{domain_term} reddit review discussion', max_results=4)

    criteria = """Score based on:
- 90-100: Frequently recommended in relevant subreddits, predominantly positive, active official presence
- 70-89: Regularly mentioned, mostly positive sentiment, some official presence
- 50-69: Mentioned in several threads, mixed sentiment, recognized by community
- 30-49: Occasional mentions, limited to 1-2 subreddits, no official presence
- 10-29: Rare mentions, largely unknown on Reddit
- 0-9: No Reddit presence"""

    analysis = analyze_with_ai(brand, "Reddit", snippets, criteria)
    
    # Force 0 if DDG failed, hallucinated, or brand not in snippets
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No Reddit presence detected."
    elif not validate_snippets(brand, snippets) and not any("reddit.com" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)

    return {
        "platform": "Reddit",
        "correlation": "High",
        "weight": "25%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.reddit.com/search/?q={brand.replace(' ', '+')}",
        "recommendations": [
            "Identify 3-5 subreddits where your target audience is active",
            "Participate authentically—do not shill",
            "Monitor and respond to brand mentions",
            "Create genuinely helpful posts that demonstrate expertise",
        ]
    }


def check_wikipedia(brand: str, url: str = "") -> dict:
    """Check Wikipedia/Wikidata brand presence via API."""
    has_wiki = False
    wiki_url = ""
    wikidata_id = ""
    domain = extract_domain(url)

    # Check Wikipedia API directly — require EXACT title match (case-insensitive)
    try:
        from urllib.parse import quote_plus
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(brand)}&format=json"
        r = requests.get(api_url, headers={"User-Agent": "GEO-Audit/1.0"}, timeout=10)
        data = r.json()
        results = data.get("query", {}).get("search", [])
        if results:
            top_title = results[0].get("title", "")
            # Strict match: title must BE the brand name, not just contain it as a substring
            if top_title.lower().strip() == brand.lower().strip():
                has_wiki = True
                wiki_url = f"https://en.wikipedia.org/wiki/{top_title.replace(' ', '_')}"
            elif len(brand) > 3 and brand.lower() in top_title.lower():
                # For longer brand names, substring is ok
                has_wiki = True
                wiki_url = f"https://en.wikipedia.org/wiki/{top_title.replace(' ', '_')}"
    except Exception:
        pass

    # Check Wikidata — also require more explicit match for short names
    try:
        from urllib.parse import quote_plus
        wd_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote_plus(brand)}&language=en&format=json"
        r2 = requests.get(wd_url, headers={"User-Agent": "GEO-Audit/1.0"}, timeout=10)
        wd = r2.json()
        entities = wd.get("search", [])
        if entities:
            # For short brand names, verify the Wikidata label matches more closely
            wd_label = entities[0].get("label", "").lower()
            if len(brand) <= 3:
                if wd_label == brand.lower():
                    wikidata_id = entities[0].get("id", "")
            else:
                wikidata_id = entities[0].get("id", "")
    except Exception:
        pass

    # Supplement with search snippets — include domain for disambiguation
    domain_term = f" {domain}" if domain else ""
    snippets = ddg_search(f'"{brand}"{domain_term} site:wikipedia.org', max_results=4)

    criteria = f"""The brand "{brand}" {'HAS a Wikipedia article at ' + wiki_url if has_wiki else 'does NOT have a Wikipedia article'}.
{'It HAS a Wikidata entry: ' + wikidata_id if wikidata_id else 'No Wikidata entry found.'}.

Score based on:
- 90-100: Detailed Wikipedia article (B-class or higher) + Wikidata entry with complete properties
- 70-89: Wikipedia article exists + Wikidata entry
- 50-69: Wikipedia article (stub) or basic Wikidata entry
- 30-49: No Wikipedia article but mentioned in other articles; Wikidata may exist
- 10-29: 1-2 passing mentions in Wikipedia
- 0-9: No Wikipedia or Wikidata presence"""

    analysis = analyze_with_ai(brand, "Wikipedia", snippets, criteria)
    score = analysis.get("score", 0)
    # Give a baseline if confirmed Wikipedia page exists
    if has_wiki and score < 50:
        score = 60

    return {
        "platform": "Wikipedia / Wikidata",
        "correlation": "High",
        "weight": "20%",
        "score": score,
        "has_wikipedia": has_wiki,
        "wikipedia_url": wiki_url,
        "wikidata_id": wikidata_id,
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "recommendations": [
            "Build notability through press coverage first before seeking a Wikipedia article",
            "Ensure your Wikidata entry (Q-number) is complete even without a full article",
            "Contribute to industry articles where your brand can be naturally cited",
        ]
    }


def check_linkedin(brand: str, url: str = "") -> dict:
    """Check LinkedIn brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    
    snippets = ddg_search(f'"{brand}"{domain_term} site:linkedin.com/company', max_results=5)
    snippets += ddg_search(f'"{brand}"{domain_term} company linkedin followers employees', max_results=3)

    criteria = """Score based on:
- 90-100: Active company page with 10K+ followers, regular thought leadership posts
- 70-89: Active company page with 5K+ followers, some employee thought leadership
- 50-69: Company page with 1K+ followers, irregular posting
- 30-49: Company page exists but sparse/inactive
- 10-29: Basic company page with minimal information
- 0-9: No LinkedIn company page"""

    analysis = analyze_with_ai(brand, "LinkedIn", snippets, criteria)
    
    # Force 0 if DDG failed, hallucinated, or brand not in snippets
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No LinkedIn presence detected."
    elif not validate_snippets(brand, snippets) and not any("linkedin.com" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)
        
    return {
        "platform": "LinkedIn",
        "correlation": "Moderate",
        "weight": "15%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "neutral"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.linkedin.com/search/results/companies/?keywords={brand.replace(' ', '+')}",
        "recommendations": [
            "Optimize company page with complete information and regular posting",
            "Encourage leadership to post thought leadership content weekly",
            "Engage with industry discussions to increase visibility",
        ]
    }


def check_facebook(brand: str, url: str = "") -> dict:
    """Check Facebook brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    snippets = ddg_search(f'"{brand}"{domain_term} site:facebook.com', max_results=5)
    criteria = """Score based on:
- 90-100: Active verified official page with thousands of followers and regular posts
- 70-89: Official page exists with good following but moderate activity
- 50-69: Basic page exists, limited followers/posts
- 30-49: Unofficial or community pages only
- 10-29: Sparse mentions by other users
- 0-9: No Facebook presence"""
    analysis = analyze_with_ai(brand, "Facebook", snippets, criteria)
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No Facebook presence detected."
    elif not validate_snippets(brand, snippets) and not any("facebook.com" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)
    return {
        "platform": "Facebook",
        "correlation": "Moderate",
        "weight": "8%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.facebook.com/search/pages/?q={brand.replace(' ', '+')}",
        "recommendations": [
            "Create or claim your official Facebook page",
            "Post regular updates, events, and community engaging content",
            "Encourage and respond to customer reviews on Facebook",
        ]
    }

def check_instagram(brand: str, url: str = "") -> dict:
    """Check Instagram brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    snippets = ddg_search(f'"{brand}"{domain_term} site:instagram.com', max_results=5)
    criteria = """Score based on:
- 90-100: Official verified profile with thousands of followers and active engagement
- 70-89: Official profile exists, good following, moderate activity
- 50-69: Basic profile exists, limited followers/posts
- 30-49: Unofficial or hashtag mentions only
- 10-29: Sparse mentions by other users
- 0-9: No Instagram presence"""
    analysis = analyze_with_ai(brand, "Instagram", snippets, criteria)
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No Instagram presence detected."
    elif not validate_snippets(brand, snippets) and not any("instagram.com" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)
    return {
        "platform": "Instagram",
        "correlation": "Moderate",
        "weight": "8%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.instagram.com/explore/search/keyword/?q={brand.replace(' ', '+')}",
        "recommendations": [
            "Create or claim your official Instagram profile",
            "Post high-quality visual content regularly",
            "Engage with followers and relevant niche hashtags",
        ]
    }

def check_twitter(brand: str, url: str = "") -> dict:
    """Check Twitter/X brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    snippets = ddg_search(f'"{brand}"{domain_term} site:twitter.com OR site:x.com', max_results=5)
    criteria = """Score based on:
- 90-100: Official verified account with thousands of followers and active posting
- 70-89: Official account exists, good following, moderate activity
- 50-69: Basic account exists, limited followers/posts
- 30-49: Unofficial or customer chatter only
- 10-29: Sparse passing mentions by other users
- 0-9: No Twitter/X presence"""
    analysis = analyze_with_ai(brand, "Twitter/X", snippets, criteria)
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No Twitter/X presence detected."
    elif not validate_snippets(brand, snippets) and not any("twitter.com" in s for s in snippets) and not any("x.com" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)
    return {
        "platform": "Twitter/X",
        "correlation": "Moderate",
        "weight": "8%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://twitter.com/search?q={brand.replace(' ', '+')}",
        "recommendations": [
            "Create or claim your official Twitter/X account",
            "Engage proactively with industry news and customer support",
            "Post frequently to build brand authority signals",
        ]
    }

def check_tiktok(brand: str, url: str = "") -> dict:
    """Check TikTok brand presence."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    snippets = ddg_search(f'"{brand}"{domain_term} site:tiktok.com', max_results=5)
    criteria = """Score based on:
- 90-100: Official verified account with thousands of followers and viral/active content
- 70-89: Official account exists, good following, moderate activity
- 50-69: Basic account exists or many user-generated videos about brand
- 30-49: Sparse user-generated mentions
- 10-29: Extremely rare mentions
- 0-9: No TikTok presence"""
    analysis = analyze_with_ai(brand, "TikTok", snippets, criteria)
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No TikTok presence detected."
    elif not validate_snippets(brand, snippets) and not any("tiktok.com" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)
    return {
        "platform": "TikTok",
        "correlation": "Moderate",
        "weight": "8%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.tiktok.com/search?q={brand.replace(' ', '+')}",
        "recommendations": [
            "Create or claim your official TikTok profile",
            "Share engaging, short-form video content",
            "Collaborate with TikTok creators in your niche",
        ]
    }

def check_other_platforms(brand: str, url: str = "") -> dict:
    """Check other supplementary platforms (Quora, News, GitHub etc)."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    
    snippets = ddg_search(f'"{brand}"{domain_term} site:quora.com', max_results=3)
    snippets += ddg_search(f'"{brand}"{domain_term} news press coverage 2024 2025', max_results=4)
    snippets += ddg_search(f'"{brand}"{domain_term} podcast mention', max_results=3)

    criteria = """Score based on presence across Quora, news/press, GitHub, podcasts:
- 90-100: Strong press coverage, Quora answers, podcast appearances
- 70-89: Some press coverage, Quora presence
- 50-69: Limited press, a few Quora mentions
- 30-49: Minimal press, rare mentions
- 0-29: Essentially no supplementary platform presence"""

    analysis = analyze_with_ai(brand, "Other Platforms (Quora, News, Podcasts)", snippets, criteria)
    
    # Force 0 if DDG failed, hallucinated, or brand not in snippets
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["summary"] = "No supplementary platform presence detected."
    elif not validate_snippets(brand, snippets):
        analysis["score"] = min(analysis.get("score", 0), 15)

    return {
        "platform": "Other Platforms",
        "correlation": "Supplementary",
        "weight": "15%",
        "score": analysis.get("score", 0),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "recommendations": [
            "Create Quora answers for top industry questions related to your brand",
            "Issue press releases for major company milestones",
            "Pursue podcast guest appearances in your niche",
        ]
    }


def check_directories(brand_name: str, url: str = "") -> dict:
    """Check brand presence on major local directories."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    
    # Search for brand on specific directory sites
    snippets = ddg_search(f'"{brand_name}"{domain_term} site:yelp.com', max_results=3)
    snippets += ddg_search(f'"{brand_name}"{domain_term} site:yellowpages.com', max_results=3)
    snippets += ddg_search(f'"{brand_name}"{domain_term} site:trustpilot.com', max_results=3)
    snippets += ddg_search(f'"{brand_name}"{domain_term} local directory business listing', max_results=3)

    criteria = """Score based on presence across Yelp, YellowPages, Trustpilot, etc:
- 90-100: Verified listings on 3+ major directories with positive reviews
- 70-89: Listings on 2 major directories, mostly positive
- 50-69: Listing on 1 major directory or several smaller niche directories
- 30-49: Sparse mentions in directories, no verified listings
- 0-29: No identifiable local directory presence"""

    analysis = analyze_with_ai(brand_name, "Local Directories", snippets, criteria)
    
    # Force 0 if DDG failed, hallucinated, or brand not in snippets
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No local directory presence detected."
    elif not validate_snippets(brand_name, snippets):
        analysis["score"] = min(analysis.get("score", 0), 15)

    return {
        "platform": "Local Directories",
        "correlation": "High (Local Entity)",
        "weight": "20%",
        "score": analysis.get("score", 0),
        "has_listings": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "neutral"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "recommendations": [
            "Claim your business profile on Yelp and YellowPages",
            "Encourage happy customers to leave reviews on Trustpilot",
            "Ensure NAP (Name, Address, Phone) consistency across all directories",
            "Add high-quality photos to your directory listings",
        ]
    }


def check_google_maps_presence(brand: str, url: str = "") -> dict:
    """Check brand presence on Google Maps / GBP via search snippets."""
    domain = extract_domain(url)
    domain_term = f" {domain}" if domain else ""
    
    snippets = ddg_search(f'"{brand}"{domain_term} site:google.com/maps', max_results=5)
    snippets += ddg_search(f'"{brand}"{domain_term} Google Business Profile review', max_results=3)

    criteria = """Score based on:
- 90-100: Verified Google Business Profile with 4.5+ rating and 100+ reviews
- 70-89: Verified GBP with 4.0+ rating and 20+ reviews
- 50-69: GBP exists, verified, but fewer reviews
- 30-49: Claimed but incomplete profile or low ratings
- 10-29: Unclaimed profile or passing mentions only
- 0-9: No Google Maps presence"""

    # We reuse the analyze_with_ai but with a local context focus
    analysis = analyze_with_ai(brand, "Google Maps (GBP)", snippets, criteria)
    
    # Force 0 if DDG failed, hallucinated, or brand not in snippets
    if not snippets or all("Search failed" in s for s in snippets) or "No search results found" in "\n".join(snippets):
        analysis["score"] = 0
        analysis["has_presence"] = False
        analysis["summary"] = "No Google Maps presence detected."
    elif not validate_snippets(brand, snippets) and not any("google.com/maps" in s for s in snippets):
        analysis["score"] = min(analysis.get("score", 0), 10)

    return {
        "platform": "Google Maps (GBP)",
        "correlation": "High (Local Entity)",
        "weight": "20%",
        "score": analysis.get("score", 0),
        "has_presence": analysis.get("has_presence", False),
        "sentiment": analysis.get("sentiment", "unknown"),
        "key_findings": analysis.get("key_findings", []),
        "summary": analysis.get("summary", ""),
        "search_url": f"https://www.google.com/maps/search/{brand.replace(' ', '+')}",
        "recommendations": [
            "Claim and verify your Google Business Profile",
            "Ensure NAP (Name, Address, Phone) consistency",
            "Regularly post updates and photos to your GBP",
            "Encourage customers to leave detailed, keyword-rich reviews",
        ]
    }


def calculate_brand_authority(platforms: dict) -> int:
    """Calculate composite Brand Authority Score from platform scores."""
    youtube_score = platforms.get("YouTube", {}).get("score", 0)
    reddit_score = platforms.get("Reddit", {}).get("score", 0)
    wikipedia_score = platforms.get("Wikipedia / Wikidata", {}).get("score", 0)
    linkedin_score = platforms.get("LinkedIn", {}).get("score", 0)
    directory_score = platforms.get("Local Directories", {}).get("score", 0)
    facebook_score = platforms.get("Facebook", {}).get("score", 0)
    instagram_score = platforms.get("Instagram", {}).get("score", 0)
    twitter_score = platforms.get("Twitter/X", {}).get("score", 0)
    tiktok_score = platforms.get("TikTok", {}).get("score", 0)
    other_score = platforms.get("Other Platforms", {}).get("score", 0)

    total = (
        youtube_score * 0.15
        + reddit_score * 0.15
        + wikipedia_score * 0.10
        + directory_score * 0.15
        + linkedin_score * 0.08
        + facebook_score * 0.08
        + instagram_score * 0.08
        + twitter_score * 0.08
        + tiktok_score * 0.08
        + other_score * 0.05
    )
    return min(int(total), 100)


def scan_brand(brand_name: str, url: str = "") -> dict:
    """Main entrypoint: Perform full brand scan using AI-powered analysis."""
    print(f"[brand_scanner] Starting brand analysis for: {brand_name}", file=sys.stderr)
    if url:
        print(f"[brand_scanner] Using URL for disambiguation: {url}", file=sys.stderr)

    youtube = check_youtube(brand_name, url)
    print(f"[brand_scanner] YouTube: {youtube['score']}/100", file=sys.stderr)

    reddit = check_reddit(brand_name, url)
    print(f"[brand_scanner] Reddit: {reddit['score']}/100", file=sys.stderr)

    wikipedia = check_wikipedia(brand_name, url)
    print(f"[brand_scanner] Wikipedia: {wikipedia['score']}/100", file=sys.stderr)

    linkedin = check_linkedin(brand_name, url)
    print(f"[brand_scanner] LinkedIn: {linkedin['score']}/100", file=sys.stderr)

    directories = check_directories(brand_name, url)
    print(f"[brand_scanner] Directories: {directories['score']}/100", file=sys.stderr)

    facebook = check_facebook(brand_name, url)
    print(f"[brand_scanner] Facebook: {facebook['score']}/100", file=sys.stderr)

    instagram = check_instagram(brand_name, url)
    print(f"[brand_scanner] Instagram: {instagram['score']}/100", file=sys.stderr)

    twitter = check_twitter(brand_name, url)
    print(f"[brand_scanner] Twitter/X: {twitter['score']}/100", file=sys.stderr)

    tiktok = check_tiktok(brand_name, url)
    print(f"[brand_scanner] TikTok: {tiktok['score']}/100", file=sys.stderr)

    other = check_other_platforms(brand_name, url)
    print(f"[brand_scanner] Other: {other['score']}/100", file=sys.stderr)

    google_maps = check_google_maps_presence(brand_name, url)
    print(f"[brand_scanner] Google Maps: {google_maps['score']}/100", file=sys.stderr)

    platforms = {
        "YouTube": youtube,
        "Reddit": reddit,
        "Wikipedia / Wikidata": wikipedia,
        "Facebook": facebook,
        "Instagram": instagram,
        "Twitter/X": twitter,
        "TikTok": tiktok,
        "LinkedIn": linkedin,
        "Local Directories": directories,
        "Other Platforms": other,
        "Google Maps (GBP)": google_maps,
    }

    brand_authority = calculate_brand_authority(platforms)
    print(f"[brand_scanner] Brand Authority Score: {brand_authority}/100", file=sys.stderr)

    return {
        "brand_name": brand_name,
        "url": url,
        "brand_authority_score": brand_authority,
        "platforms": platforms,
        "recommendations": [
            "Prioritize YouTube content creation—highest AI citation correlation",
            "Build authentic Reddit community presence",
            "Pursue Wikipedia notability through press coverage",
            "Maintain consistent LinkedIn posting schedule",
            "Build Quora authority in your niche",
        ]
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python brand_scanner.py <brand_name> [url]")
        sys.exit(1)

    brand = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""

    result = scan_brand(brand, url)
    print(json.dumps(result, indent=2))
