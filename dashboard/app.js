const logOutput = document.getElementById('logOutput');
const statusIndicator = document.getElementById('statusIndicator');

function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `[${timestamp}] `;
    const div = document.createElement('div');

    if (type === 'error') div.style.color = '#ff9ff3';
    if (type === 'success') div.style.color = '#55efc4';

    div.textContent = prefix + message;
    logOutput.appendChild(div);
    logOutput.scrollTop = logOutput.scrollHeight;
}

function setStatus(status, isActive = false) {
    if (!statusIndicator) return;
    statusIndicator.textContent = status;
    if (isActive) {
        statusIndicator.classList.add('active');
    } else {
        statusIndicator.classList.remove('active');
    }
}

function showView(viewId) {
    document.querySelectorAll('main').forEach(view => {
        view.style.display = 'none';
    });
    document.getElementById(viewId).style.display = 'block';
}

async function runStep(step, isSequence = false) {
    const brand = document.getElementById('brandName').value;
    const url = document.getElementById('targetUrl').value;
    const gbpUrl = document.getElementById('gbpUrl').value;

    log(`Triggering step: ${step.toUpperCase()}...`);
    setStatus(`Running ${step}`, true);

    try {
        const response = await fetch('/api/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ step, brand, url, gbpUrl })
        });

        const data = await response.json();

        if (data.status === 'success') {
            log(`${step.toUpperCase()} completed successfully.`, 'success');
            if (data.output) log(data.output);
            return { success: true, data: data };
        } else {
            log(`Error in ${step}: ${data.error}`, 'error');
            return { success: false };
        }
    } catch (e) {
        log(`Failed to execute ${step}: ${e}`, 'error');
        return { success: false };
    } finally {
        if (!isSequence) setStatus('Ready');
    }
}

document.getElementById('runFullAudit').addEventListener('click', async () => {
    await runFullAuditSequence(false);
});

document.getElementById('runAutoAudit').addEventListener('click', async () => {
    await runFullAuditSequence(true);
});

async function runFullAuditSequence(isAutoFlow = false) {
    const brand = document.getElementById('brandName').value || "Orbis Local";
    const url = document.getElementById('targetUrl').value || "https://google.com";
    const gbpUrl = document.getElementById('gbpUrl').value;

    log(`=== Starting Full Audit Sequence for ${brand} ===`);

    if (isAutoFlow) {
        showView('generatingView');
        document.getElementById('generatingBrand').textContent = brand;
        const scannerLine = document.querySelector('.scanner-line');
        if (scannerLine) scannerLine.style.display = 'block';
        startGeneratingAnimations();
    } else {
        setStatus(`Full Audit In Progress`, true);
    }

    const steps = ['fetch', 'score', 'brand', 'crawlers', 'gbp', 'report'];
    let success = true;

    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];

        // Update UI initially to begin the stage
        if (isAutoFlow) {
            updateGeneratingProgress(step, i, steps.length);
        } else {
            updateDashboardProgress(step, i, steps.length);
        }

        const result = await runStep(step, true);
        if (result.success) {
            const btn = document.querySelector(`button[onclick="runStep('${step}')"]`);
            if (btn) btn.classList.add('completed');

            // Re-render live data based on output from specific steps!
            if (isAutoFlow && result.data && result.data.output) {
                try {
                    const parsedObj = JSON.parse(result.data.output);

                    if (step === 'score' && parsedObj.average_citability_score !== undefined) {
                        const aiPrefVal = parsedObj.average_citability_score;
                        const scoreStr = parseInt(aiPrefVal) + "%";
                        // Update bar1: AI PREF
                        document.querySelector('#bar1').style.height = aiPrefVal + '%';
                        document.querySelector('#bar1').parentElement.querySelector('.bar-val').textContent = scoreStr;
                    }
                    else if (step === 'gbp' && parsedObj.overall_local_score !== undefined) {
                        const trustVal = parsedObj.overall_local_score;
                        const scoreStr = parseInt(trustVal) + "%";
                        // Update bar3: TRUST
                        document.querySelector('#bar3').style.height = trustVal + '%';
                        document.querySelector('#bar3').parentElement.querySelector('.bar-val').textContent = scoreStr;
                    }
                    else if (step === 'brand' && parsedObj.platforms) {
                        // SGE 2026 can be derived from Brand Authority platforms 'Google AI Overviews' or ChatGPT
                        let platScore = 0;
                        if (parsedObj.platforms["Google AI Overviews"]) {
                            platScore = parseInt(parsedObj.platforms["Google AI Overviews"].score || parsedObj.platforms["Google AI Overviews"].weight || "0");
                        }
                        const scoreStr = platScore + "%";
                        // Update bar2: SGE 2026
                        document.querySelector('#bar2').style.height = platScore + '%';
                        document.querySelector('#bar2').parentElement.querySelector('.bar-val').textContent = scoreStr;
                    }
                } catch (e) {
                    // ignore JSON parse error
                }
            }
        } else {
            success = false;
            break;
        }
    }

    if (success) {
        // Force 100% completion state at the very end
        if (isAutoFlow) {
            updateGeneratingProgress('report', steps.length, steps.length);
        }
        log('FULL AUDIT COMPLETE!', 'success');
        if (isAutoFlow) {
            showView('leadGenView');
        }
    } else {
        log('Audit sequence aborted due to an error.', 'error');
        if (isAutoFlow) {
            alert('Audit aborted due to an error. Please check the dashboard console.');
            showView('dashboardView');
        }
    }

    setStatus('Ready');
}

function updateDashboardProgress(step, index, total) {
    // Legacy dashboard progress update if needed, but we removed the progress Box from HTML
}

function updateGeneratingProgress(step, index, total) {
    const progressFill = document.getElementById('subProgressBar');
    const percentCounter = document.getElementById('percentCounter');
    const progressPercent = Math.round((index / total) * 100);

    if (progressFill) progressFill.style.width = progressPercent + '%';
    if (percentCounter) percentCounter.textContent = progressPercent + '%';

    // Update dots
    const stageEl = document.getElementById(`stage-${step}`);
    if (stageEl) {
        const previouslyActive = document.querySelector('.stage.active');
        if (previouslyActive) {
            previouslyActive.classList.remove('active');
            previouslyActive.classList.add('complete');
        }
        stageEl.classList.add('active');
    }
}

// Global steps definition for helper functions
const steps = ['fetch', 'score', 'brand', 'crawlers', 'gbp', 'report'];

function startGeneratingAnimations() {
    const aiMessages = [
        "AI isn't just a trend; it's the 2026 search baseline.",
        "85% of users prefer AI-summarized results for quick answers.",
        "Getting in the AI game now future-proofs your brand authority.",
        "Generative engines prioritize brands with high 'entity density'.",
        "Your competitors are already optimizing for Perplexity and SGE.",
        "AI Citability is the new SEO Backlink.",
        "Orbis Local ensures your brand is the 'First Choice' for AI answers.",
        "2026 Search: Conversational, Immediate, and Personal.",
        "Stop 'ranking' and start 'being cited' by the world's top LLMs.",
        "AI-ready content has a 3x higher click-through rate in modern search."
    ];

    const stats = [
        "85% of Users Prefer AI Summaries",
        "72% Higher Trust in AI-Cited Brands",
        "90% Growth in Conversational Search",
        "65% Local Visibility via GEO Engines",
        "AI Answers drive 4x higher purchase intent"
    ];

    let msgTitleIdx = 0;
    let msgStatIdx = 0;

    // Clear any existing intervals
    if (window.generatingIntervals) {
        window.generatingIntervals.forEach(clearInterval);
    }
    window.generatingIntervals = [];

    // Reset stages
    document.querySelectorAll('.stage').forEach(s => {
        s.classList.remove('active', 'complete');
    });

    // Reset bars
    document.querySelectorAll('.bar').forEach(b => {
        b.style.height = '0';
        setTimeout(() => {
            b.style.height = b.getAttribute('data-h') + '%';
        }, 500);
    });

    // Rotate Messages
    const msgInterval = setInterval(() => {
        msgTitleIdx = (msgTitleIdx + 1) % aiMessages.length;
        const box = document.getElementById('strategyBox');
        if (box) {
            box.style.opacity = 0;
            box.style.transform = "translateY(-10px)";
            setTimeout(() => {
                box.textContent = aiMessages[msgTitleIdx];
                box.style.opacity = 1;
                box.style.transform = "translateY(0)";
            }, 500);
        }
    }, 4500);
    window.generatingIntervals.push(msgInterval);

    // Rotate Stats
    const statInterval = setInterval(() => {
        msgStatIdx = (msgStatIdx + 1) % stats.length;
        const statEl = document.getElementById('statLabel');
        if (statEl) statEl.textContent = stats[msgStatIdx];
    }, 6000);
    window.generatingIntervals.push(statInterval);
}

// Lead Gen Form Submission
document.getElementById('leadGenForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // In a real app, we'd send this to a CRM
    const name = document.getElementById('leadName').value;
    const email = document.getElementById('leadEmail').value;
    const phone = document.getElementById('leadPhone').value;
    const brand = document.getElementById('brandName').value;
    const url = document.getElementById('targetUrl').value;
    const consent = document.getElementById('leadConsent').checked;

    const submitBtn = document.querySelector('#leadGenForm button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Verifying...';
    submitBtn.disabled = true;

    try {
        // Persist lead to server and verify email
        const response = await fetch('/api/lead', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, brand, url, consent })
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Failed to submit form. Please check your data.");
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
            return;
        }

        log(`Lead captured: ${name} (${email}) - Marketing Consent: ${consent}`, 'success');

        showView('reportView');
        const scannerLine = document.querySelector('.scanner-line');
        if (scannerLine) scannerLine.style.display = 'none';

        const reportFrame = document.getElementById('reportFrame');
        // Load the PDF report into the iframe
        reportFrame.src = '/api/view-report';

    } catch (err) {
        console.error("Failed to save lead:", err);
        alert("An unexpected error occurred. Please try again.");
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

document.getElementById('clearLogs').addEventListener('click', () => {
    logOutput.innerHTML = 'Waiting for command...';
    setStatus('Ready');
});
