const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const nodemailer = require('nodemailer');

const app = express();
const port = 3000;

// Setup email transporter for Leads
const transporter = nodemailer.createTransport({
    host: 'mail.spacemail.com',
    port: 465,
    secure: true,
    auth: {
        user: 'insights@orbislocal.com',
        pass: 'Orbis@8214@@!!'
    }
});

app.use(express.json());

// Redirect index.html to /
app.get('/index.html', (req, res) => {
    res.redirect(301, '/');
});

app.use(express.static(path.join(__dirname, '.')));
app.use('/reports', express.static(path.join(__dirname, '..')));

// Helper to run python scripts
function runScript(scriptPath, args, res) {
    const process = spawn('python', [scriptPath, ...args], { cwd: path.join(__dirname, '..') });

    let output = '';
    let error = '';

    // Set a timeout of 120 seconds
    const timeout = setTimeout(() => {
        process.kill();
        console.error(`Script timed out: ${scriptPath}`);
        if (!res.headersSent) {
            res.status(500).json({ status: 'error', error: `Script execution timed out (120s). Partial output: ${error}` });
        }
    }, 120000);

    process.stdout.on('data', (data) => {
        output += data.toString();
        console.log(`STDOUT: ${data}`);
    });

    process.stderr.on('data', (data) => {
        error += data.toString();
        console.error(`STDERR: ${data}`);
    });

    process.on('close', (code) => {
        clearTimeout(timeout);
        const trimmedOutput = output.trim();
        if (code === 0) {
            try {
                const parsed = JSON.parse(trimmedOutput);

                // Check if the JSON itself contains an error
                if (parsed.error) {
                    return res.status(500).json({ status: 'error', error: parsed.error });
                }

                // If this is one of our data scripts, save the output to file for the PDF generator
                const fs = require('fs');
                if (scriptPath.includes('fetch_page')) fs.writeFileSync(path.join(__dirname, '..', 'test_fetch.json'), trimmedOutput);
                if (scriptPath.includes('citability_scorer')) fs.writeFileSync(path.join(__dirname, '..', 'test_citability.json'), trimmedOutput);
                if (scriptPath.includes('llmstxt_generator')) fs.writeFileSync(path.join(__dirname, '..', 'test_llms.json'), trimmedOutput);
                if (scriptPath.includes('brand_scanner')) fs.writeFileSync(path.join(__dirname, '..', 'test_brand.json'), trimmedOutput);
                if (scriptPath.includes('gbp_analyzer')) fs.writeFileSync(path.join(__dirname, '..', 'test_gbp.json'), trimmedOutput);

                res.json({ status: 'success', output: trimmedOutput });
            } catch (e) {
                // If it's not JSON (e.g., PDF gen output), check for error keywords
                if (trimmedOutput.toLowerCase().includes('error')) {
                    return res.status(500).json({ status: 'error', error: trimmedOutput });
                }
                res.json({ status: 'success', raw: trimmedOutput });
            }
        } else {
            res.status(500).json({ status: 'error', code, error: error || 'Script exited with non-zero code' });
        }
    });
}

// API: Run Full Audit (Sequential)
app.post('/api/audit', async (req, res) => {
    const { url, brand, gbpUrl } = req.body;
    if (!url || !brand) return res.status(400).json({ error: 'URL and Brand required' });

    console.log(`Starting Full Audit for ${url} (${brand})`);

    // In a real production app, we would use a task queue and WebSockets for real-time logs.
    // For this basic dashboard, we'll run them and return a final status.
    try {
        // Step 1: Brand Scan
        const run = (cmd, args) => new Promise((resolve, reject) => {
            const p = spawn('python', [cmd, ...args], { cwd: path.join(__dirname, '..') });
            let output = '';
            p.stdout.on('data', d => output += d);
            p.stderr.on('data', d => console.error(d.toString()));

            p.on('close', (code) => {
                if (code === 0) {
                    try {
                        const str = output.trim();
                        JSON.parse(str);
                        const fs = require('fs');
                        if (cmd.includes('fetch_page')) fs.writeFileSync(path.join(__dirname, '..', 'test_fetch.json'), str);
                        if (cmd.includes('citability_scorer')) fs.writeFileSync(path.join(__dirname, '..', 'test_citability.json'), str);
                        if (cmd.includes('llmstxt_generator')) fs.writeFileSync(path.join(__dirname, '..', 'test_llms.json'), str);
                        if (cmd.includes('brand_scanner')) fs.writeFileSync(path.join(__dirname, '..', 'test_brand.json'), str);
                        if (cmd.includes('gbp_analyzer')) fs.writeFileSync(path.join(__dirname, '..', 'test_gbp.json'), str);
                    } catch (e) { }
                    resolve();
                } else {
                    reject(`Step ${cmd} failed`);
                }
            });
        });

        if (process.env.OUTSCRAPER_API_KEY) {
            triggerOutscraperTask('contacts', url || brand);
            if (gbpUrl) triggerOutscraperTask('maps', gbpUrl);
        }

        await run('scripts/brand_scanner.py', [brand]);
        await run('scripts/fetch_page.py', [url]);
        await run('scripts/citability_scorer.py', [url]);
        await run('scripts/llmstxt_generator.py', [url]);
        if (gbpUrl) {
            await run('scripts/gbp_analyzer.py', [gbpUrl]);
            await run('scripts/gbp_grid.py', [brand, gbpUrl]);
        }
        await run('scripts/generate_live_pdf.py', []);

        res.json({ status: 'Complete', message: 'Full Audit and PDF Report generated successfully.' });
    } catch (e) {
        res.status(500).json({ status: 'Error', message: e.toString() });
    }
});

// Outscraper Webhook Trigger Helper
async function triggerOutscraperTask(type, query) {
    const apiKey = process.env.OUTSCRAPER_API_KEY;
    if (!apiKey) return null;

    const webhookUrl = "https://audit.myorbislocal.com/api/webhooks/outscraper";
    let endpoint = "";

    if (type === 'maps') {
        endpoint = `https://api.outscraper.com/maps/search-v3?query=${encodeURIComponent(query)}&async=true&webhook=${encodeURIComponent(webhookUrl)}`;
    } else if (type === 'contacts') {
        endpoint = `https://api.outscraper.com/emails-and-contacts?query=${encodeURIComponent(query)}&async=true&webhook=${encodeURIComponent(webhookUrl)}`;
    } else {
        return null;
    }

    try {
        // Node 18+ has native fetch
        const response = await fetch(endpoint, {
            headers: { 'X-API-KEY': apiKey }
        });
        const data = await response.json();
        console.log(`[Outscraper] Triggered ${type} task for "${query}". Task ID: ${data.id || 'unknown'}`);
        return data.id;
    } catch (e) {
        console.error(`[Outscraper] Error triggering ${type}:`, e);
        return null;
    }
}

// API: Run Specific Step

app.post('/api/step', (req, res) => {
    const { step, brand, url, gbpUrl } = req.body;

    const scripts = {
        'fetch': ['scripts/fetch_page.py', [url]],
        'score': ['scripts/citability_scorer.py', [url]],
        'brand': ['scripts/brand_scanner.py', [brand, url || '']],
        'crawlers': ['scripts/llmstxt_generator.py', [url]],
        'gbp': ['scripts/gbp_analyzer.py', [gbpUrl]],
        'grid': ['scripts/gbp_grid.py', [brand, gbpUrl]],
        'report': ['scripts/generate_live_pdf.py', []]
    };

    if (!scripts[step]) return res.status(400).json({ error: 'Invalid step' });

    runScript(scripts[step][0], scripts[step][1], res);
});

// API: Outscraper Webhook
app.post('/api/webhooks/outscraper', async (req, res) => {
    // Outscraper sends results here when async scraping tasks finish
    const payload = req.body;

    if (!payload || !payload.id) {
        return res.status(400).json({ error: 'Invalid Outscraper payload' });
    }

    const taskId = payload.id;
    const taskStatus = payload.status;
    const data = payload.data || [];

    console.log(`[Webhook] Received Outscraper data for task ${taskId} (Status: ${taskStatus})`);

    const fs = require('fs');
    const path = require('path');

    // Attempt to determine if this is Google Maps data or Emails & Contacts data
    // based on the structure of the returned objects in the first result
    let taskType = 'unknown';
    if (data.length > 0 && data[0] && Array.isArray(data[0])) {
        const item = data[0][0]; // Outscraper often returns an array of arrays
        if (item && item.type) {
            taskType = 'maps';
        } else if (item && item.emails !== undefined) {
            taskType = 'contacts';
        }
    } else if (data.length > 0 && data[0]) {
        // Alternative structure
        const item = data[0];
        if (item.type) taskType = 'maps';
        else if (item.emails !== undefined) taskType = 'contacts';
    }

    // Save the raw verified data to be ingested by the python scripts later
    const outputPath = path.join(__dirname, '..', `outscraper_${taskType}_${taskId}.json`);
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));

    // Maintain a master reference of completed verified data
    const masterRefPath = path.join(__dirname, '..', 'outscraper_results.json');
    let resultsRef = {};
    if (fs.existsSync(masterRefPath)) {
        try {
            resultsRef = JSON.parse(fs.readFileSync(masterRefPath));
        } catch (e) { }
    }

    resultsRef[taskId] = {
        type: taskType,
        status: taskStatus,
        file: outputPath,
        updatedAt: new Date().toISOString()
    };

    fs.writeFileSync(masterRefPath, JSON.stringify(resultsRef, null, 2));

    res.json({ status: 'success', received: true });
});

// API: GBP Grid Data Directly
app.get('/api/gbp-grid-data', (req, res) => {
    const fs = require('fs');
    const path = require('path');
    const gridPath = path.join(__dirname, '..', 'test_gbp_grid.json');
    if (fs.existsSync(gridPath)) {
        res.json(JSON.parse(fs.readFileSync(gridPath)));
    } else {
        res.json(null);
    }
});

// API: Simulation Engine Data Directly
app.get('/api/simulation-data', (req, res) => {
    const fs = require('fs');
    const path = require('path');
    const simPath = path.join(__dirname, '..', 'test_sim.json');
    if (fs.existsSync(simPath)) {
        res.json(JSON.parse(fs.readFileSync(simPath)));
    } else {
        res.json(null);
    }
});

// API: Run GEO Simulation (Baseline vs Optimized comparison)
app.post('/api/simulate', (req, res) => {
    const { brand, lat, lng, score } = req.body;
    if (!brand || !lat || !lng) {
        return res.status(400).json({ error: 'brand, lat, and lng are required' });
    }
    const args = [brand, String(lat), String(lng), String(score || 50)];
    runScript('scripts/sim_engine.py', args, res);
});


// API: View/Download Report
app.get('/api/view-report', (req, res) => {
    const filePath = path.join(__dirname, '..', 'ORBIS-LOCAL-LIVE-REPORT.pdf');
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'inline; filename="ORBIS-LOCAL-LIVE-REPORT.pdf"');
    res.sendFile(filePath);
});

// API: Save Lead
app.post('/api/lead', async (req, res) => {
    const { name, email, phone, brand, url, consent } = req.body;

    // Verify Email with Reoon API
    try {
        // We use dynamic import for node-fetch if fetch isn't available, but Node 18+ has fetch built-in
        const verifyResponse = await fetch(`https://emailverifier.reoon.com/api/v1/verify?key=ufdAYB7hnnSr2idfjNZOr6gKW2dmfb2U&mode=quick&email=${encodeURIComponent(email)}`);
        const verifyResult = await verifyResponse.json();

        // Reoon returns status: "safe", "valid", "invalid", "disposable", "role_account", "catch_all"
        // We want to reject outright invalid or disposable emails.
        if (verifyResult.status === 'invalid' || verifyResult.status === 'disposable' || verifyResult.status === 'spamtrap') {
            return res.status(400).json({ error: `Email verification failed: Address is ${verifyResult.status}. Please use a valid business email.` });
        }
    } catch (e) {
        console.error("Email verification service error (proceeding anyway):", e);
    }

    const fs = require('fs');
    const leadsPath = path.join(__dirname, '..', 'leads.json');

    let leads = [];
    if (fs.existsSync(leadsPath)) {
        try {
            leads = JSON.parse(fs.readFileSync(leadsPath));
        } catch (e) {
            console.error("Error reading leads.json:", e);
        }
    }

    leads.push({
        name, email, phone, brand, url, consent,
        timestamp: new Date().toISOString()
    });

    fs.writeFileSync(leadsPath, JSON.stringify(leads, null, 2));

    // Send admin email notification
    const adminMailOptions = {
        from: '"Orbis Local Auditor" <insights@orbislocal.com>',
        to: 'insights@myorbislocal.com',
        subject: `New Enterprise Audit Lead: ${name} - ${brand || 'Unknown Brand'}`,
        text: `A new lead has completed the Orbis Local Enterprise AI Search Visibility Auditor.\n\n` +
            `Contact Details:\n` +
            `Name: ${name}\n` +
            `Email: ${email}\n` +
            `Phone: ${phone}\n` +
            `Brand/Company: ${brand || 'N/A'}\n` +
            `Target URL: ${url}\n` +
            `Marketing Consent: ${consent ? 'Yes' : 'No'}\n\n` +
            `This lead has been saved to your local leads.json file.`
    };

    transporter.sendMail(adminMailOptions, (error, info) => {
        if (error) {
            console.error("Failed to send admin lead email notification:", error);
        } else {
            console.log("Admin lead email notification sent:", info.messageId);
        }
    });

    // Send subscriber email with PDF attachment
    const subscriberMailOptions = {
        from: '"Orbis Local Auditor" <insights@orbislocal.com>',
        to: email,
        subject: `Your Orbis Local AI Search Visibility Report`,
        html: `
            <p>Hi ${name},</p>
            <p>Thank you for requesting your Enterprise AI Search Visibility Audit.</p>
            <p>I've attached your custom report directly to this email so you can review your current visibility scores across the AI ecosystem.</p>
            <p>I want to be completely transparent with you: as we move deeper into 2026, the shift to AI-driven search is accelerating rapidly. If you aren't actively optimizing for visibility on platforms like Google AI Overviews, ChatGPT, Perplexity, and Claude AI right now, it may soon be too late to gain ground.</p>
            <p>Think of it this way—someone is likely talking to your competitors right now about how to capture this exact market share, just like I'm speaking with you.</p>
            <p>Take a look at the report, and let's get ahead of the curve before your competitors beat you to the punch.</p>
            <br>
            <p>Best regards,</p>
            <p><strong>The Orbis Local Team</strong></p>
        `,
        attachments: [
            {
                filename: 'ORBIS-LOCAL-LIVE-REPORT.pdf',
                path: path.join(__dirname, '..', 'ORBIS-LOCAL-LIVE-REPORT.pdf')
            }
        ]
    };

    transporter.sendMail(subscriberMailOptions, (error, info) => {
        if (error) {
            console.error("Failed to send subscriber email with report:", error);
        } else {
            console.log("Subscriber email sent successfully:", info.messageId);
        }
    });

    res.json({ status: 'success' });
});

app.listen(port, () => {
    console.log(`Orbis Local Dashboard running at http://localhost:${port}`);
});
