from playwright.sync_api import sync_playwright

def scrape_address(url):
    print(f"Playwright scraping: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            
            address = page.evaluate('''() => {
                const btn = document.querySelector('button[data-item-id="address"]');
                if (btn) return btn.getAttribute('aria-label') || btn.innerText;
                const divs = Array.from(document.querySelectorAll('div'));
                for (let d of divs) {
                    if (d.innerText && d.innerText.match(/,\\s*[A-Z]{2}\\s*\\d{5}/)) return d.innerText;
                }
                return "";
            }''')
            
            print(f"Output: {address.replace('Address: ', '').strip()}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_address("https://maps.app.goo.gl/EEKjPP9oKbUENTkR8")
