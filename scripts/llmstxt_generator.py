#!/usr/bin/env python3
"""
llms.txt Generator — Creates and validates llms.txt files for AI crawler guidance.

The llms.txt standard is an emerging specification that helps AI crawlers
understand your site structure and find your most important content.

Location: /llms.txt (root of domain)
Extended: /llms-full.txt (detailed version)
"""

import sys
import json
import re
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed. Run: pip install requests beautifulsoup4")
    sys.exit(1)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def validate_llmstxt(url: str) -> dict:
    """Check if llms.txt exists and validate its format."""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    llms_url = f"{base_url}/llms.txt"
    llms_full_url = f"{base_url}/llms-full.txt"

    result = {
        "url": llms_url,
        "exists": False,
        "format_valid": False,
        "has_title": False,
        "has_description": False,
        "has_sections": False,
        "has_links": False,
        "section_count": 0,
        "link_count": 0,
        "content": "",
        "issues": [],
        "suggestions": [],
        "full_version": {
            "url": llms_full_url,
            "exists": False,
        },
    }

    # Check llms.txt
    try:
        # Check for cached content first
        html_content = None
        import os
        cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_fetch.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                if cache_data.get("url") == llms_url: # Unlikely as fetch_page fetches home
                    html_content = cache_data.get("raw_html")

        if not html_content:
            response = requests.get(llms_url, headers=DEFAULT_HEADERS, timeout=15)
            if response.status_code == 200:
                html_content = response.text
            else:
                result["issues"].append(f"llms.txt returned status {response.status_code}")

        if html_content:
            result["exists"] = True
            result["content"] = html_content
            content = html_content

            # Validate format
            lines = content.strip().split("\n")

            # Check for title (# at start)
            if lines and lines[0].startswith("# "):
                result["has_title"] = True
            else:
                result["issues"].append("Missing title (should start with '# Site Name')")

            # Check for description (> blockquote)
            for line in lines:
                if line.startswith("> "):
                    result["has_description"] = True
                    break
            if not result["has_description"]:
                result["issues"].append("Missing description (use '> Brief description')")

            # Check for sections (## headings)
            sections = [l for l in lines if l.startswith("## ")]
            result["section_count"] = len(sections)
            result["has_sections"] = len(sections) > 0
            if not result["has_sections"]:
                result["issues"].append("No sections found (use '## Section Name')")

            # Check for links
            link_pattern = r"- \[.+\]\(.+\)"
            links = re.findall(link_pattern, content)
            result["link_count"] = len(links)
            result["has_links"] = len(links) > 0
            if not result["has_links"]:
                result["issues"].append("No page links found (use '- [Page Title](url): Description')")

            # Overall format validity
            result["format_valid"] = (
                result["has_title"]
                and result["has_description"]
                and result["has_sections"]
                and result["has_links"]
            )

            # Suggestions
            if result["link_count"] < 5:
                result["suggestions"].append("Consider adding more key pages (aim for 10-20)")
            if result["section_count"] < 2:
                result["suggestions"].append("Add more sections to organize content types")
            if "contact" not in content.lower():
                result["suggestions"].append("Add a Contact section with email and location")
            if "key fact" not in content.lower() and "about" not in content.lower():
                result["suggestions"].append("Add key facts about your business/service")

        else:
            result["issues"].append(f"llms.txt returned status {response.status_code}")
    except Exception as e:
        result["issues"].append(f"Error fetching llms.txt: {str(e)}")

    # Check llms-full.txt
    try:
        response = requests.get(llms_full_url, headers=DEFAULT_HEADERS, timeout=15)
        if response.status_code == 200:
            result["full_version"]["exists"] = True
    except Exception:
        pass

    return result


def generate_llmstxt(url: str, max_pages: int = 30) -> dict:
    """Generate an llms.txt file by crawling the site."""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    result = {
        "generated_llmstxt": "",
        "generated_llmstxt_full": "",
        "pages_analyzed": 0,
        "sections": {},
    }

    # Discover and categorize pages
    # Check for cached content from fetch_page script
    soup = None
    try:
        import os
        cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_fetch.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                if cache_data.get("url") == url and "raw_html" in cache_data:
                    soup = BeautifulSoup(cache_data["raw_html"], "lxml")
    except Exception:
        pass

    if not soup:
        # Fetch homepage
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            result["error"] = f"Failed to fetch homepage: {str(e)}"
            return result

    # Extract site name and description
    title = soup.find("title")
    site_name = title.get_text(strip=True).split("|")[0].split("-")[0].strip() if title else parsed.netloc
    meta_desc = soup.find("meta", attrs={"name": "description"})
    site_description = meta_desc.get("content", "") if meta_desc else f"Official website of {site_name}"

    # Discover and categorize pages
    pages = {
        "Main Pages": [],
        "Products & Services": [],
        "Resources & Blog": [],
        "Company": [],
        "Support": [],
    }

    # Crawl internal links
    seen_urls = set()
    for link in soup.find_all("a", href=True):
        href = urljoin(base_url, link["href"])
        link_text = link.get_text(strip=True)

        if not link_text or len(link_text) < 2:
            continue

        parsed_href = urlparse(href)
        if parsed_href.netloc != parsed.netloc:
            continue
        if href in seen_urls:
            continue
        if any(ext in href for ext in [".pdf", ".jpg", ".png", ".gif", ".css", ".js"]):
            continue
        if "#" in href and href.split("#")[0] in seen_urls:
            continue

        seen_urls.add(href)
        path = parsed_href.path.lower()

        # Categorize
        page_entry = {"url": href, "title": link_text}

        if any(kw in path for kw in ["/pricing", "/features", "/product", "/solutions", "/demo"]):
            pages["Products & Services"].append(page_entry)
        elif any(kw in path for kw in ["/blog", "/article", "/resource", "/guide", "/learn", "/docs", "/documentation"]):
            pages["Resources & Blog"].append(page_entry)
        elif any(kw in path for kw in ["/about", "/team", "/career", "/contact", "/press", "/partner"]):
            pages["Company"].append(page_entry)
        elif any(kw in path for kw in ["/help", "/support", "/faq", "/status"]):
            pages["Support"].append(page_entry)
        elif path in ["/", ""] or any(kw in path for kw in ["/home", "/index"]):
            if href != base_url and href != base_url + "/":
                pages["Main Pages"].append(page_entry)
        else:
            pages["Main Pages"].append(page_entry)

        if len(seen_urls) >= max_pages:
            break

    result["pages_analyzed"] = len(seen_urls)

    # Generate llms.txt (concise version)
    llms_lines = [
        f"# {site_name}",
        f"> {site_description}",
        "",
    ]

    for section, section_pages in pages.items():
        if section_pages:
            llms_lines.append(f"## {section}")
            # Limit to top 10 per section for concise version
            for page in section_pages[:10]:
                llms_lines.append(f"- [{page['title']}]({page['url']})")
            llms_lines.append("")

    # Add contact section placeholder
    llms_lines.extend([
        "## Contact",
        f"- Website: {base_url}",
        f"- Email: contact@{parsed.netloc}",
        "",
    ])

    result["generated_llmstxt"] = "\n".join(llms_lines)

    # Generate llms-full.txt (detailed version with descriptions)
    full_lines = [
        f"# {site_name}",
        f"> {site_description}",
        "",
    ]

    for section, section_pages in pages.items():
        if section_pages:
            full_lines.append(f"## {section}")
            for page in section_pages:
                # Try to fetch page description
                try:
                    page_resp = requests.get(page["url"], headers=DEFAULT_HEADERS, timeout=10)
                    page_soup = BeautifulSoup(page_resp.text, "lxml")
                    page_meta = page_soup.find("meta", attrs={"name": "description"})
                    page_desc = page_meta.get("content", "") if page_meta else ""
                    if page_desc:
                        full_lines.append(f"- [{page['title']}]({page['url']}): {page_desc}")
                    else:
                        full_lines.append(f"- [{page['title']}]({page['url']})")
                except Exception:
                    full_lines.append(f"- [{page['title']}]({page['url']})")
            full_lines.append("")

    full_lines.extend([
        "## Contact",
        f"- Website: {base_url}",
        f"- Email: contact@{parsed.netloc}",
        "",
    ])

    result["generated_llmstxt_full"] = "\n".join(full_lines)
    result["sections"] = {k: len(v) for k, v in pages.items()}

    return result



# All major AI crawlers and which platform they serve
AI_CRAWLERS = {
    "GPTBot": {"platform": "ChatGPT / OpenAI", "docs": "https://platform.openai.com/docs/gptbot"},
    "ChatGPT-User": {"platform": "ChatGPT Browsing", "docs": "https://platform.openai.com/docs/plugins/bot"},
    "ClaudeBot": {"platform": "Anthropic Claude", "docs": "https://support.anthropic.com/en/articles/8896518"},
    "anthropic-ai": {"platform": "Anthropic AI", "docs": "https://support.anthropic.com/"},
    "PerplexityBot": {"platform": "Perplexity AI", "docs": "https://docs.perplexity.ai/docs/perplexitybot"},
    "Googlebot": {"platform": "Google (AI Overviews)", "docs": "https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers"},
    "Google-Extended": {"platform": "Google Gemini / Bard", "docs": "https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers"},
    "Bingbot": {"platform": "Bing / Copilot", "docs": "https://www.bing.com/webmaster/help/which-crawlers-does-bing-use"},
    "cohere-ai": {"platform": "Cohere AI", "docs": "https://cohere.com"},
    "YouBot": {"platform": "You.com AI Search", "docs": "https://you.com"},
    "Applebot": {"platform": "Apple Siri / AI Features", "docs": "https://support.apple.com/en-us/111900"},
    "Meta-ExternalAgent": {"platform": "Meta AI", "docs": "https://www.meta.com"},
}


def check_ai_crawlers(url: str) -> dict:
    """Fetch robots.txt and determine which AI crawlers are allowed/blocked."""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base_url}/robots.txt"

    result = {
        "robots_url": robots_url,
        "robots_found": False,
        "crawlers": {},
    }

    robots_text = ""
    try:
        response = requests.get(robots_url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code == 200:
            result["robots_found"] = True
            robots_text = response.text
    except Exception as e:
        result["error"] = f"Could not fetch robots.txt: {e}"
        robots_text = ""

    # Parse robots.txt into per-agent rules
    # Simple parser: track current user-agent and whether Disallow: / is set
    agent_rules: dict[str, list[str]] = {}
    current_agents: list[str] = []
    global_disallows: list[str] = []
    in_global = False

    for line in robots_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            if current_agents:
                current_agents = []
            continue

        if line.lower().startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agents.append(agent)
            if agent not in agent_rules:
                agent_rules[agent] = []
            in_global = (agent == "*")

        elif line.lower().startswith("disallow:") and current_agents:
            path = line.split(":", 1)[1].strip()
            for a in current_agents:
                agent_rules.setdefault(a, []).append(("disallow", path))
            if in_global:
                global_disallows.append(path)

        elif line.lower().startswith("allow:") and current_agents:
            path = line.split(":", 1)[1].strip()
            for a in current_agents:
                agent_rules.setdefault(a, []).append(("allow", path))

    def is_allowed(agent_name: str) -> tuple[str, str]:
        """Return (status, detail) for a specific crawler."""
        if not result["robots_found"]:
            return "Unknown", "robots.txt not found — crawler access is likely allowed by default"

        rules = agent_rules.get(agent_name, [])

        # Check for explicit full-block: Disallow: /
        for rule_type, path in rules:
            if rule_type == "disallow" and path in ["/", ""]:
                return "Blocked", f"Explicitly blocked via 'Disallow: /' for {agent_name}"
            if rule_type == "disallow" and path:
                return "Partial", f"Some paths blocked ({path}) for {agent_name}"

        if rules:
            return "Allowed", f"Agent {agent_name} found in robots.txt with no full blocks"

        # No explicit rule — fall back to global * rules
        for path in global_disallows:
            if path == "/":
                return "Blocked", f"Blocked via wildcard 'Disallow: /' (no explicit {agent_name} rule)"

        return "Allowed", f"No explicit rule for {agent_name} — inheriting global allow"

    for agent_key, meta in AI_CRAWLERS.items():
        status, detail = is_allowed(agent_key)
        result["crawlers"][agent_key] = {
            "platform": meta["platform"],
            "status": status,
            "recommendation": (
                f"Add 'Allow: /' rule for {agent_key} in robots.txt"
                if status == "Blocked"
                else ("Consider explicitly allowing this crawler" if status == "Unknown" else "No action needed")
            ),
            "detail": detail,
        }

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python llmstxt_generator.py <url> [mode]")
        print("Modes: validate (default), generate, crawlers")
        sys.exit(1)

    target_url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "validate"

    if mode == "validate":
        llms_data = validate_llmstxt(target_url)
        crawler_data = check_ai_crawlers(target_url)
        combined = {**llms_data, **crawler_data}
        print(json.dumps(combined, indent=2, default=str))
    elif mode == "generate":
        data = generate_llmstxt(target_url)
        print(json.dumps(data, indent=2, default=str))
    elif mode == "crawlers":
        data = check_ai_crawlers(target_url)
        print(json.dumps(data, indent=2, default=str))
    else:
        print(f"Unknown mode: {mode}. Use 'validate', 'generate', or 'crawlers'.")
        sys.exit(1)

