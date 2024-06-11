from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import urllib.parse

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


scopes = os.getenv("SCOPES", "user-read-private user-read-email")
redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8888/callback")

auth_query_parameters = {
    "response_type": "code",
    "client_id": client_id,
    "scope": scopes,
    "redirect_uri": redirect_uri,
    "show_dialog": "true"
}
auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(auth_query_parameters)
print("Go to the following URL to authorize the application:")
print(auth_url)


def get_token():
    auth_code = input("Enter auth code: ")
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_profile_info(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

token = get_token()
print(token)
profile = get_profile_info(token)
print(profile)


