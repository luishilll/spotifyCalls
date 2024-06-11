from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import urllib.parse
import webbrowser


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


scopes = os.getenv("SCOPES", "user-read-private user-read-email")
redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8888/callback")

def get_auth_url():
    auth_query_parameters = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scopes,
        "redirect_uri": redirect_uri,
        "show_dialog": "true"
    }

    return "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(auth_query_parameters)

def get_token(code):

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
        "code": code,
        "redirect_uri": redirect_uri
    }
    result = post(url, headers=headers, data=data)
    token = json.loads(result.content)["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def get_recent_tracks(token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = get_auth_header(token)
    query = "?limit=50"

    result = get(url + query, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

if __name__ == '__main__':
    auth_url = get_auth_url()
    print("Please go to this URL and authorize the application:")
    print(auth_url)

    # Open the URL in the default web browser
    webbrowser.open(auth_url)

    # Get the authorization code from the user
    code = input("Enter the authorization code: ")

    # Exchange the authorization code for an access token
    token = get_token(code)

    # Get and print the user's recently played tracks
    recent_tracks = get_recent_tracks(token)
    print(json.dumps(recent_tracks, indent=4))


