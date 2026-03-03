import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

url = 'http://localhost:3000/api/lead'
headers = {'Content-Type': 'application/json'}
payload = {
    "name": "Test User",
    "email": "insights@myorbislocal.com", 
    "phone": "555-0199",
    "brand": "Test Brand",
    "url": "https://example.com",
    "consent": True
}

try:
    logging.info(f"Sending POST to {url} with payload {payload}")
    response = requests.post(url, headers=headers, json=payload)
    logging.info(f"Response Status Code: {response.status_code}")
    logging.info(f"Response Body: {response.text}")
except Exception as e:
    logging.error(f"Failed to connect: {e}", exc_info=True)
