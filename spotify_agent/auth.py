import time
import requests
from dotenv import load_dotenv
import os
import json
import base64
from langchain_core.tools import tool

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN_PATH = "access_token.json"

@tool
def get_access_token():
    if os.path.exists(ACCESS_TOKEN_PATH):
        with open(ACCESS_TOKEN_PATH,'r') as f:
            token_data = json.load(f)
            if time.time()< token_data["expires_at"]:
                return token_data['access_token']
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    base64_str = base64.b64encode(auth_str.encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {base64_str}"},
        data={"grant_type": "client_credentials"},)
    data = response.json()
    if "access_token" not in data:
        print("Error from Spotify API:")
        print(data)
        return None
    access_token = data['access_token']
    expires_in = data['expires_in']
    expires_at = expires_in + time.time() - 60
    with open(ACCESS_TOKEN_PATH,'w') as f:
        json.dump({
            "access_token":access_token,
            "expires_at":expires_at
        },f)
    return access_token
