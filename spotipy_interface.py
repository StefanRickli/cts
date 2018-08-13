import sys
import spotipy
import spotipy.util as util
import urllib.parse
import app_data

scope = 'user-library-read user-read-playback-state user-modify-playback-state'

username = app_data.username()

client_id = app_data.client_id()
client_secret = app_data.client_secret()
redirect_uri = app_data.redirect_url()

def get_authenticated_spotify():
    token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    if token:
        return spotipy.Spotify(auth = token)
    else:
        raise("Can't get token for {}".format(username))

def sp_login():
    util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

def sp_find(song_artist, song_title):
    sp = get_authenticated_spotify()

    query = str(song_artist) + ' ' + str(song_title)
    results = sp.search(query, limit=10, offset=0, type='track')

    track_results = results['tracks']

    if track_results['total'] == 0:
        return None
    else:
        return track_results['items']


def sp_play(items, items_offset):
    sp = get_authenticated_spotify()

    uris = []
    for song in items:
        uris.append(song['uri'])
    sp.start_playback(uris = uris, offset = {'position': items_offset})
    sp.repeat('track')


def sp_pause_resume():
    sp = get_authenticated_spotify()

    pb = sp.current_playback()
    if pb['is_playing']:
        sp.pause_playback()
    else:
        sp.start_playback()
    
def sp_skip(direction):
    sp = get_authenticated_spotify()

    if direction == 1:
        sp.next_track()
    else:
        sp.previous_track()

def sp_seek(direction):
    sp = get_authenticated_spotify()

    pb = sp.current_playback()
    current_song = sp.track(pb['item']['uri'])
    song_length_ms = current_song['duration_ms']

    if pb['is_playing']:
        t_ms = pb['progress_ms']
        if direction == 1:
            if song_length_ms - t_ms > 7000:
                sp.seek_track(min(t_ms + 5000, song_length_ms))
        else:
            sp.seek_track(max(t_ms - 5000, 0))



