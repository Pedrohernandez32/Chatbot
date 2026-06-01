import requests
import json

response = requests.post(
    'http://localhost:9999/api/chat',
    json={'message': 'sistemas'},
    headers={'Content-Type': 'application/json'}
)

print("Status:", response.status_code)
print("Response:", response.text)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
