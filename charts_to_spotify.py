# MAIN FILE
# Displays a GUI to facilitate adding songs from arbitrary chart lists to one's Spotify playlists

import sys
import logging
from asciimatics.screen import Screen
from spotipy_wrapper import SpotipyWrapper, TimeoutError, NoActiveDeviceError, WrongUserError
from requests import ConnectionError
import spotipy_interface
import app_data
import app_config

config = {}

def pre_gui():
    spotify = login(config['username'])

    return spotify


def login(username):
    spotify = SpotipyWrapper(username)
    
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


class GuiLauncher:
    def __init__(self):
        self.screen = None
        self.spotify = None

    def go(self, screen):
        self.screen = screen


class ChartsChoice:
    def __init__(self):
        pass

    def show(self):
        pass


class MainMenu:
    def __init__(self, spotify, charts_items):
        self.charts_items = charts_items
        self.sp = spotify

    def show(self):
        pass

    def spotify_find(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    config = app_config.load_config()

    spotipy_wrapper_handle = pre_gui()
    launcher = GuiLauncher()
    launcher.spotify = spotipy_wrapper_handle

    Screen.wrapper(launcher.go)

    app_config.save_config(config)
