import requests
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Hello! Can you confirm this key works?"
                }
            ]
        }
    ]
}

response = requests.post(ENDPOINT, headers=headers, json=data)

if response.status_code == 200:
    print("✅ API key is valid. Response:")
    print(response.json())
else:
    print(f"❌ Failed. Status Code: {response.status_code}")
    print(response.text)
