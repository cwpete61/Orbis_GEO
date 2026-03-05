---
phase: 18
plan: 1
wave: 1
---

# Wave 1: Verification Infrastructure

Implement the core API connection and webhook listener to handle Outscraper's asynchronous data delivery.

## Context
- `dashboard/server.js`: Needs a new POST endpoint for webhooks.
- `.env`: Needs `OUTSCRAPER_API_KEY`.

## Tasks

### 1. Webhook Implementation
Add a POST `/api/webhooks/outscraper` route to `server.js`.
- [ ] Parse the JSON body.
- [ ] If `status === "SUCCESS"`, log the `results_location`.
- [ ] Save the incoming webhook payload to `test_outscraper_webhook.json`.

### 2. API Trigger
Update the audit flow to call Outscraper and provide the webhook URL.
- [ ] Implement a helper to trigger `Google Maps Data` and `Emails & Contacts Scraper`.
- [ ] Use `https://audit.myorbislocal.com/api/webhooks/outscraper` as the callback.

## Verification
- [ ] Send a mock POST request to `/api/webhooks/outscraper`.
- [ ] Verify `test_outscraper_webhook.json` is created correctly.
