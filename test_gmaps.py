import requests
import json
from bs4 import BeautifulSoup

def extract_schema_address(url):
    print(f"Resolving: {url}")
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        res = session.get(url, headers=headers, allow_redirects=True, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        print("\nSearching for LD+JSON Schema...")
        # Google Maps sometimes embeds standard LocalBusiness schema
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if '@type' in data and data['@type'] in ['LocalBusiness', 'Organization', 'Place']:
                    print(json.dumps(data.get('address', {}), indent=2))
                    return data.get('address')
            except Exception as e:
                pass
                
        print("No LD+JSON schema found.")
        
        # Another approach: find the exact address text natively rendered in the DOM
        # Often div or span containing the address has a specific class, but it varies.
        # Just rip all text and look for the zip code 18102
        print("\nScanning raw document text for the ZIP code...")
        all_text = soup.get_text(separator=' | ')
        import re
        matches = re.findall(r'[^|]*18102[^|]*', all_text)
        if matches:
            print("Found potential address snippets in text:")
            for m in set(matches):
                print(f"-> {m.strip()}")
                
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    extract_schema_address("https://maps.app.goo.gl/EEKjPP9oKbUENTkR8")
