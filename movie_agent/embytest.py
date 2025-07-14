import requests
import json

emby_server = "https://emby.thamilxerox.com/emby"
api_key = "715a43b7c82448dc9456c52172d6be45"
username = "root"

url = f"{emby_server}/Users"
res = requests.get(url, params={'api_key': api_key})
users = res.json()

for user in users:
    if user["Name"].lower() == username.lower():
        print(f"✅ User ID for '{username}': {user['Id']}")
