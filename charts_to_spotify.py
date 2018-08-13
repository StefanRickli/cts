# MAIN FILE
# Displays a GUI to facilitate adding songs from arbitrary chart lists to one's Spotify playlists

import sys
import logging
from asciimatics.screen import Screen
from spotipy_wrapper import SpotipyWrapper, TimeoutError, NoActiveDeviceError, WrongUserError
from requests import ConnectionError
import spotipy_interface
import app_data

def pre_gui():
    spotify = SpotipyWrapper(app_data.username())
    
    login_succeeded = False
    while not login_succeeded:
        try:
            spotify.login()
            login_succeeded = True
        except WrongUserError:
            logging.error("Login NOT SUCCESSFUL. Check which user is logged in on https://open.spotify.com")
        except TimeoutError:
            c = input("Login didn't succeed, retry? [Y,N]")
            if c in ('n', 'N'):
                sys.exit()
        except ConnectionError as e:
            logging.error(str(e))
    
    return spotify


def gui_launcher(screen):
    pass


class chart_choice:
    def __init__(self):
        pass

    def show(self):
        pass


class main_menu:
    def __init__(self, spotify, charts_items):
        self.charts_items = charts_items
        self.sp = spotify

    def show(self):
        pass

    def spotify_find(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    spotify = pre_gui()
    
    Screen.wrapper(gui_launcher)
