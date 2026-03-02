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

    process.stdout.on('data', (data) => {
        output += data.toString();
        console.log(`STDOUT: ${data}`);
    });

    process.stderr.on('data', (data) => {
        error += data.toString();
        console.error(`STDERR: ${data}`);
    });

    process.on('close', (code) => {
        if (code === 0) {
            try {
                // Try to parse JSON if it's a data script
                res.json({ status: 'success', output: output.trim() });
            } catch (e) {
                res.json({ status: 'success', raw: output });
            }
        } else {
            res.status(500).json({ status: 'error', code, error });
        }
    });
}

// API: Run Full Audit (Sequential)
app.post('/api/audit', async (req, res) => {
    const { url, brand } = req.body;
    if (!url || !brand) return res.status(400).json({ error: 'URL and Brand required' });

    console.log(`Starting Full Audit for ${url} (${brand})`);

    // In a real production app, we would use a task queue and WebSockets for real-time logs.
    // For this basic dashboard, we'll run them and return a final status.
    try {
        // Step 1: Brand Scan
        const run = (cmd, args) => new Promise((resolve, reject) => {
            const p = spawn('python', [cmd, ...args], { cwd: path.join(__dirname, '..') });
            p.on('close', (code) => code === 0 ? resolve() : reject(`Step ${cmd} failed`));
        });

        await run('scripts/brand_scanner.py', [brand]);
        await run('scripts/fetch_page.py', [url]);
        await run('scripts/citability_scorer.py', [url]);
        await run('scripts/llmstxt_generator.py', [url]);
        await run('scripts/generate_pdf_report.py', []);

        res.json({ status: 'Complete', message: 'Full Audit and PDF Report generated successfully.' });
    } catch (e) {
        res.status(500).json({ status: 'Error', message: e.toString() });
    }
});

// API: Run Specific Step
app.post('/api/step', (req, res) => {
    const { step, brand, url } = req.body;

    const scripts = {
        'fetch': ['scripts/fetch_page.py', [url]],
        'score': ['scripts/citability_scorer.py', [url]],
        'brand': ['scripts/brand_scanner.py', [brand]],
        'crawlers': ['scripts/llmstxt_generator.py', [url]],
        'report': ['scripts/generate_pdf_report.py', []]
    };

    if (!scripts[step]) return res.status(400).json({ error: 'Invalid step' });

    runScript(scripts[step][0], scripts[step][1], res);
});

app.listen(port, () => {
    console.log(`Orbis Local Dashboard running at http://localhost:${port}`);
});
