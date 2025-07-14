import os
import json
import time
import requests
import base64
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_CLIENT_REDIRECT_URL")
SCOPE = "user-read-recently-played user-read-playback-state playlist-read-private playlist-read-collaborative user-library-read"
ACCESS_TOKEN_PATH = "access_token.json"

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful. You can close this window.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Authorization failed. No code received.</h1>")


def start_local_server():
    server = HTTPServer(("localhost", 3000), AuthHandler)
    thread = Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

def get_auth_code():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    print(f"Open this URL in your browser:\n{auth_url}")
    print("Visit this URL:", auth_url)
    print("CLIENT_ID =", CLIENT_ID)
    print("REDIRECT_URI =", REDIRECT_URI)


    
    server = start_local_server()

    while not getattr(server, "auth_code", None):
        time.sleep(1)

    code = server.auth_code
    server.shutdown()
    return code

def exchange_code_for_token(code):
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64_auth}"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )
    data = response.json()
    if "access_token" not in data:
        raise Exception("Token exchange failed: " + str(data))
    
    expires_at = time.time() + data["expires_in"] - 60
    data["expires_at"] = expires_at

    with open(ACCESS_TOKEN_PATH, 'w') as f:
        json.dump(data, f)
    print("Token exchange response:", response.status_code, response.text)

    return data["access_token"]

def refresh_token(refresh_token):
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64_auth}"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    data = response.json()
    if "access_token" not in data:
        raise Exception("Refresh failed: " + str(data))
    
    with open(ACCESS_TOKEN_PATH, 'r') as f:
        old_data = json.load(f)

    data["refresh_token"] = data.get("refresh_token", old_data["refresh_token"])
    data["expires_at"] = time.time() + data["expires_in"] - 60

    with open(ACCESS_TOKEN_PATH, 'w') as f:
        json.dump(data, f)

    return data["access_token"]

def get_access_token():
    if os.path.exists(ACCESS_TOKEN_PATH):
        with open(ACCESS_TOKEN_PATH, 'r') as f:
            data = json.load(f)
            if time.time() < data.get("expires_at", 0):
                return data["access_token"]
            else:
                return refresh_token(data["refresh_token"])
    else:
        code = get_auth_code()
        return exchange_code_for_token(code)


if __name__ == "__main__":
    token = get_access_token()
    print("Access token:", token)
    import sys
    sys.exit(0)
