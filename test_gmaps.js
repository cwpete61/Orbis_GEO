const puppeteer = require('puppeteer');

(async () => {
    const url = 'https://maps.app.goo.gl/EEKjPP9oKbUENTkR8';
    console.log(`Launching Puppeteer to resolve: ${url}`);

    // Launch a headless browser
    const browser = await puppeteer.launch({ headless: "new" });
    const page = await browser.newPage();

    // Set a normal user agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    // Go to the URL and wait for the network to be idle (so React can render the DOM)
    console.log("Navigating and waiting for DOM...");
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Google Maps usually stores the address in an element with a specific aria-label
    // Or we can just look for the element containing the city and state
    console.log("Evaluating the DOM...");
    const address = await page.evaluate(() => {
        // Try finding the button that contains the address text.
        // Google Maps address buttons almost always have a data-item-id starting with "address"
        const addressBtn = document.querySelector('button[data-item-id="address"]');
        if (addressBtn) {
            return addressBtn.getAttribute('aria-label') || addressBtn.innerText;
        }

        // Fallback: search all divs for a characteristic string pattern like ", ST ZIP"
        const allDivs = Array.from(document.querySelectorAll('div'));
        for (let div of allDivs) {
            if (div.innerText && div.innerText.match(/,\s*[A-Z]{2}\s*\d{5}/)) {
                return div.innerText;
            }
        }
        return "Could not find address in DOM.";
    });

    console.log(`\nAddress Found via Puppeteer:\n${address}`);

    await browser.close();
})();
