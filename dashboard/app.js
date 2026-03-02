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
    statusIndicator.textContent = status;
    if (isActive) {
        statusIndicator.classList.add('active');
    } else {
        statusIndicator.classList.remove('active');
    }
}

async function runStep(step) {
    const brand = document.getElementById('brandName').value;
    const url = document.getElementById('targetUrl').value;

    log(`Triggering manual step: ${step.toUpperCase()}...`);
    setStatus(`Running ${step}`, true);

    try {
        const response = await fetch('/api/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ step, brand, url })
        });

        const data = await response.json();

        if (data.status === 'success') {
            log(`${step.toUpperCase()} completed successfully.`, 'success');
            if (data.output) log(data.output);
        } else {
            log(`Error in ${step}: ${data.error}`, 'error');
        }
    } catch (e) {
        log(`Failed to execute ${step}: ${e}`, 'error');
    } finally {
        setStatus('Ready');
    }
}

document.getElementById('runFullAudit').addEventListener('click', async () => {
    await runFullAuditSequence(false);
});

document.getElementById('runAutoAudit').addEventListener('click', async () => {
    await runFullAuditSequence(true);
});

document.getElementById('openPdf').addEventListener('click', () => {
    window.open('/reports/GEO-REPORT-sample.pdf', '_blank');
});

async function runFullAuditSequence(autoOpen = false) {
    const brand = document.getElementById('brandName').value;
    const url = document.getElementById('targetUrl').value;

    log(`=== Starting Full Audit Sequence for ${brand} ===`);
    setStatus('Full Audit In Progress', true);

    try {
        const response = await fetch('/api/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, url })
        });

        const data = await response.json();

        if (response.ok) {
            log('FULL AUDIT COMPLETE!', 'success');
            log(data.message);
            log('Check project root for results (JSON + PDF).', 'success');

            if (autoOpen) {
                log('Auto-opening PDF report...', 'info');
                window.open('/reports/GEO-REPORT-sample.pdf', '_blank');
            }
        } else {
            log(data.message || 'Error occurred during audit.', 'error');
        }
    } catch (e) {
        log(`Audit trigger failed: ${e}`, 'error');
    } finally {
        setStatus('Ready');
    }
}

document.getElementById('clearLogs').addEventListener('click', () => {
    logOutput.innerHTML = 'Waiting for command...';
    setStatus('Ready');
});
