import requests
import json

base_url = 'http://localhost:3000/api/step'
headers = {'Content-Type': 'application/json'}

steps = ['brand', 'fetch', 'score', 'crawlers', 'gbp', 'report']

payload = {
    "brand": "Orbis Local",
    "url": "https://orbislocal.com",
    "gbpUrl": "https://g.page/orbislocal"
}

for step in steps:
    payload['step'] = step
    print(f"Testing step: {step}...")
    try:
        response = requests.post(base_url, headers=headers, json=payload)
        print(f"[{step}] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[{step}] Error Response: {response.text}")
            break
        else:
            print(f"[{step}] Success.")
    except Exception as e:
        print(f"[{step}] Request Failed: {e}")
        break
