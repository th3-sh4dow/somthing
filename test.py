# test_request.py
import requests

url = "http://192.168.31.74:5000/ask"  # Use your actual IP
payload = {
    "query": "what is games and how to play it?"
}

response = requests.post(url, json=payload)

print("[Status]:", response.status_code)
print("[Response]:", response.json())
