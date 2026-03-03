const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, '.')));
app.use('/reports', express.static(path.join(__dirname, '..')));

// Helper to run python scripts
function runScript(scriptPath, args, res) {
    const process = spawn('python', [scriptPath, ...args], { cwd: path.join(__dirname, '..') });

    let output = '';
    let error = '';

    // Set a timeout of 60 seconds
    const timeout = setTimeout(() => {
        process.kill();
        console.error(`Script timed out: ${scriptPath}`);
        if (!res.headersSent) {
            res.status(500).json({ status: 'error', error: 'Script execution timed out (60s)' });
        }
    }, 60000);

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

        await run('scripts/brand_scanner.py', [brand]);
        await run('scripts/fetch_page.py', [url]);
        await run('scripts/citability_scorer.py', [url]);
        await run('scripts/llmstxt_generator.py', [url]);
        if (gbpUrl) await run('scripts/gbp_analyzer.py', [gbpUrl]);
        await run('scripts/generate_live_pdf.py', []);

        res.json({ status: 'Complete', message: 'Full Audit and PDF Report generated successfully.' });
    } catch (e) {
        res.status(500).json({ status: 'Error', message: e.toString() });
    }
});

// API: Run Specific Step
app.post('/api/step', (req, res) => {
    const { step, brand, url, gbpUrl } = req.body;

    const scripts = {
        'fetch': ['scripts/fetch_page.py', [url]],
        'score': ['scripts/citability_scorer.py', [url]],
        'brand': ['scripts/brand_scanner.py', [brand]],
        'crawlers': ['scripts/llmstxt_generator.py', [url]],
        'gbp': ['scripts/gbp_analyzer.py', [gbpUrl]],
        'report': ['scripts/generate_live_pdf.py', []]
    };

    if (!scripts[step]) return res.status(400).json({ error: 'Invalid step' });

    runScript(scripts[step][0], scripts[step][1], res);
});

// API: View/Download Report
app.get('/api/view-report', (req, res) => {
    const filePath = path.join(__dirname, '..', 'ORBIS-LOCAL-LIVE-REPORT.pdf');
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', 'inline; filename="ORBIS-LOCAL-LIVE-REPORT.pdf"');
    res.sendFile(filePath);
});

// API: Save Lead
app.post('/api/lead', (req, res) => {
    const { name, email, phone, brand, url } = req.body;
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
        name, email, phone, brand, url,
        timestamp: new Date().toISOString()
    });

    fs.writeFileSync(leadsPath, JSON.stringify(leads, null, 2));
    res.json({ status: 'success' });
});

app.listen(port, () => {
    console.log(`Orbis Local Dashboard running at http://localhost:${port}`);
});
