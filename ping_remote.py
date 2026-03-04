import requests

url = "http://147.93.183.4:3000/api/step"
headers = {"Content-Type": "application/json"}
payload = {
    "step": "brand",
    "brand": "Orbis Local",
    "url": "https://orbislocal.com"
}

steps = ['brand', 'fetch', 'score', 'crawlers', 'gbp', 'report']

for step in steps:
    payload['step'] = step
    print(f"Testing step: {step}...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        print(f"[{step}] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[{step}] Error Response: {response.text}")
        else:
            print(f"[{step}] Success.")
    except Exception as e:
        print(f"[{step}] Request Failed: {e}")
        break
