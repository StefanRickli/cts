import sys
import os
import spotipy
import spotipy.util as util
import urllib.parse
import app_data
import logging
import multiprocessing
import time

class TimeoutError(Exception):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)

class NoActiveDeviceError(Exception):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)

class WrongUserError(Exception):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)

# Removes first positional argument, treats it as multiprocessing.Queue
# and uses that to pass on the asynchronously called target_function's
# return value
def queue_return(target_function, *args, **kwargs):
    if not isinstance(args[0], multiprocessing.queues.Queue):
        raise ValueError('Expected a Queue')
    
    result = target_function(*args[1:], **kwargs)
    args[0].put(result)

def call_with_timeout(target_function, args = (), kwargs = {}, timeout = 5, timeout_msg = 'undefined'):
    q = multiprocessing.Queue()

    # Start bar as a process
    p = multiprocessing.Process(target = queue_return(target_function, *((q,) + args), **kwargs))
    p.start()

    # Wait for timeout seconds or until process finishes
    p.join(timeout)

    # If thread is still active
    if p.is_alive():
        logging.warning('Function {}: Timeout ({})'.format(target_function.__name__, timeout))

        # Terminate
        p.terminate()
        p.join()

        raise TimeoutError(timeout_msg)
    else:
        return q.get()


scope = 'user-library-read user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private'

class SpotipyWrapper:
    def __init__(self, username):
        self.username = username
        self.client_id = app_data.client_id()
        self.client_secret = app_data.client_secret()
        self.redirect_uri = app_data.redirect_url()
        self.sp = None

    def login(self):
        token = call_with_timeout(util.prompt_for_user_token,
                                    args = (self.username, scope, self.client_id, self.client_secret, self.redirect_uri),
                                    timeout_msg = 'Timeout during Spotify token generation')
        
        if token:
            self.sp = call_with_timeout(spotipy.Spotify,
                                        kwargs = {'auth': token},
                                        timeout_msg = 'Timeout during Spotify authentication')
            
            current_user = call_with_timeout(self.sp.current_user,
                                                timeout_msg = "Timeout while retrieving current user's info")
            
            if self.username not in (current_user['id'], current_user['display_name']) :
                if current_user['display_name'] is None:
                    name_str = current_user['id']
                else:
                    name_str = '{}/{}'.format(current_user['id'], current_user['display_name'])
                
                if os.path.exists('.cache-' + self.username):
                    os.remove('.cache-' + self.username)
                
                raise WrongUserError("User's Spotify display name '{}' doesn't match the username '{}' provided to this application.\nGo to open.spotify.com and check who's logged in.".format(name_str, self.username))

            logging.debug('SpotipyWrapper.login: Login successful')
        else:
            raise IOError('Authentication error for {}'.format(self.username))

    def add(self, song, playlist):
        response = call_with_timeout(self.sp.user_playlist_add_tracks,
                                    args = (self.username, playlist['uri'], [song['uri']]),
                                    timeout_msg = 'Timeout while adding song "{}" to Spotify playlist "{}"'.format(song['name'], playlist['name']))

        logging.debug('SpotipyWrapper.add: Spotify Response: {}'.format(response))
        return response

    def find(self, song_artist, song_title):
        query = str(song_artist) + ' ' + str(song_title)
        results = call_with_timeout(self.sp.search,
                                    args = (query,),
                                    kwargs = {'limit': 10, 'offset':0, 'type': 'track'},
                                    timeout_msg = 'Timeout while performing search for song "{}" by "{}"'.format(str(song_title), str(song_artist)))

        track_results = results['tracks']

        if track_results['total'] == 0:
            logging.debug('SpotipyWrapper.find: Found no song "{}" by "{}"'.format(str(song_title), str(song_artist)))
            return None
        else:
            logging.debug('SpotipyWrapper.add: Found {} results for "{}" by "{}"'.format(track_results['total'], str(song_title), str(song_artist)))
            return track_results['items']

    def has_available_device(self):
        response = call_with_timeout(self.sp.devices,
                                            timeout_msg = 'Timeout while retrieving list of active devices on Spotify')
        print(response)
        return response['devices'] != []

    def play(self, items, items_offset):
        if not self.has_available_device():
            raise NoActiveDeviceError

        uris = []
        for song in items:
            uris.append(song['uri'])
        call_with_timeout(self.sp.start_playback,
                            kwargs = {'uris': uris, 'offset': {'position': items_offset}},
                            timeout_msg = 'Timeout while starting playback on Spotify')
        call_with_timeout(self.sp.repeat,
                            args = ('track',),
                            timeout_msg = 'Timeout while setting repeat mode on Spotify')


    def pause_resume(self):
        print('pause_resume: start')
        if not self.has_available_device():
            raise NoActiveDeviceError

        pb = call_with_timeout(self.sp.current_playback,
                                timeout_msg = 'Timeout while getting Spotify player status')

        if pb['is_playing']:
            call_with_timeout(self.sp.pause_playback,
                                timeout_msg = 'Timeout while issuing Spotify player pause')
        else:
            call_with_timeout(self.sp.start_playback,
                                timeout_msg = 'Timeout while issuing Spotify player resume')
        print('pause_resume: end')

    def skip(self, direction):
        if not self.has_available_device():
            raise NoActiveDeviceError

        if direction == 1:
            call_with_timeout(self.sp.next_track,
                                timeout_msg = 'Timeout while issuing Spotify player skip forward')
        else:
            call_with_timeout(self.sp.previous_track,
                                timeout_msg = 'Timeout while issuing Spotify player skip backward')

    def seek(self, direction):
        if not self.has_available_device():
            raise NoActiveDeviceError

        pb = call_with_timeout(self.sp.current_playback,
                                timeout_msg = 'Timeout while retrieving Spotify player status')

        if pb['is_playing']:
            current_song = call_with_timeout(self.sp.track,
                                                args = (pb['item']['uri'],),
                                                timeout_msg = 'Timeout while retrieving information about current song')
            
            song_length_ms = current_song['duration_ms']

            t_ms = pb['progress_ms']
            if direction == 1:
                if song_length_ms - t_ms > 7000:
                    call_with_timeout(self.sp.seek_track,
                                        args = (min(t_ms + 5000, song_length_ms),),
                                        timeout_msg = 'Timeout while issuing Spotify player seek forward')
            else:
                call_with_timeout(self.sp.seek_track,
                                    args = (max(t_ms - 5000, 0),),
                                    timeout_msg = 'Timeout while issuing Spotify player seek backward')



