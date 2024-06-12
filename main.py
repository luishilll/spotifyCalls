from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import urllib.parse
import webbrowser
import datetime
import subprocess



load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


scopes = os.getenv("SCOPES", "user-read-private user-read-email user-read-recently-played")
redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8888/callback")


def open_in_incognito(url):
    command = f'start chrome --incognito "{url}"'
    subprocess.run(command, shell=True)

def get_auth_url():
    auth_query_parameters = {
        "show_dialog": "true",
        "response_type": "code",
        "client_id": client_id,
        "scope": scopes,
        "redirect_uri": redirect_uri
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


def get_recent_tracks(url,headers,params=None,all_tracks=None):
    # if all_tracks is None:
    #     all_tracks = []
    # response = get(url,headers=headers)
    # data = response.json()
    #
    # if 'items' in data:
    #     all_tracks.extend(data['items'])
    #
    # if 'next' in data and data['next']:
    #     return get_recent_tracks(data['next'], headers, all_tracks=all_tracks)

    all_tracks = []
    while True:
        response = get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch recently played tracks: {response.status_code} {response.text}")
            return None

        data = response.json()
        if 'items' in data:
            all_tracks.extend(data['items'])

        # Check if there are more pages to fetch
        if 'next' in data and data['next']:
            url = data['next']
        else:
            break

    print(f"Fetched {len(all_tracks)} tracks in total.")

    print(data)
    return all_tracks


if __name__ == '__main__':
    auth_url = get_auth_url()
    print("Please go to this URL and authorize the application:")
    print(auth_url)

    # Open the URL in the default web browser
    open_in_incognito(auth_url)

    # Get the authorization code from the user
    code = input("Enter the authorization code: ")

    # Exchange the authorization code for an access token
    token = get_token(code)

    # Get and print the user's recently played tracks
    headers = get_auth_header(token)

    params = {
        "limit": 50,
        "after": int(datetime.datetime(2024, 1, 1).timestamp()) * 1000
    }
    url = "https://api.spotify.com/v1/me/player/recently-played"
    all_tracks = get_recent_tracks(url,headers,params=params)
    total_mins = [item['track']['duration_ms']/60000 for item in all_tracks]
    for item in total_mins:
        print(item)


