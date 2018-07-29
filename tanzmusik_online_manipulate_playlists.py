# from: http://www.eventghost.net/forum/viewtopic.php?t=9891#
# look further: http://spotipy.readthedocs.io/en/latest/#features

import json
import base64
import requests
import sys
import pickle
from pathlib import Path
import app_data

def getAccessToken():
    #USER VARIABLES
    refresh_token = app_data.refresh_token()
    client_id = app_data.client_id()
    client_secret = app_data.client_secret()
    ##
    
    url = 'https://accounts.spotify.com/api/token'
    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    auth_str = (client_id + ':' + client_secret).encode('ascii')
    auth_base64 = base64.standard_b64encode(auth_str)
    headers = {'Authorization': 'Basic ' + auth_base64.decode('ascii')}

    r = requests.post(url, payload, headers=headers)
    json_string = r.content
    parsed_json = json.loads(json_string)

    newtoken = parsed_json['access_token']

    pickle.dump(newtoken, open('access_token.pkl', 'wb'))

    return

#USER VARIABLES
username = "ermv5n27l47r61zmoelgeocq6"
playlistID = "1nYqtfbchAimmJbYrMX6T5"
##

if not Path('access_token.pkl').exists():
    getAccessToken()

accessToken = pickle.load(open('access_token.pkl', 'rb'))

trackInfo = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers={"Authorization": "Bearer " + accessToken})

if trackInfo.status_code == 401:
    getAccessToken()
    accessToken = pickle.load(open('access_token.pkl', 'rb'))
    trackInfo = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers={"Authorization": "Bearer " + accessToken})

if trackInfo.status_code == 204:
    print("No track info found!")
    sys.exit()

#Parse track info
i=trackInfo.json()
trackID=i['item']['id']
trackName=i['item']['name']
trackArtist=i['item']['album']['artists'][0]['name']
##

#Get playlist name
playlist = requests.get("https://api.spotify.com/v1/users/" + username + "/playlists/" + playlistID + "?fields=name", headers={"Authorization": "Bearer " + accessToken})
p = playlist.json()
pname = p['name']

#Get playlist contents
tracklist = requests.get("https://api.spotify.com/v1/users/" + username + "/playlists/" + playlistID + "/tracks?fields=items(track.id),total", headers={"Accept": "application/json", "Authorization": "Bearer " + accessToken + "\"" })
t = tracklist.json()
total = t['total']

print("Checking for duplicates...")

#Check for duplicates
offset = 100
while (offset < total):
    tracklist = requests.get("https://api.spotify.com/v1/users/" + username + "/playlists/" + playlistID + "/tracks?fields=items(track.id),total&offset=" + str(offset), headers={"Accept": "application/json", "Authorization": "Bearer " + accessToken + "\"" })
    t = tracklist.json()
    for i, song in enumerate(t['items']):
        if song['track']['id'] == trackID:
            print("Duplicate found!")
            sys.exit()
    offset +=100

print("No duplicates found.")

#Add track to playlist
add = requests.post("https://api.spotify.com/v1/users/" + username + "/playlists/" + playlistID + "/tracks?uris=spotify%3Atrack%3A" + trackID, headers={"Accept": "application/json", "Authorization": "Bearer " + accessToken + "\"" })
##



#Exit with error if song couldn't be added to playlist
if add.status_code != 201:
    print("POST ERROR: " + str(add.status_code) + " " + add.reason)
    sys.exit()
##

#Show OSD if everything went well
print("\"" + trackArtist + " - " + trackName + "\" added to playlist \"" + pname + "\".")
