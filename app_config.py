import sys
import os
import yaml
import logging
import collections
import app_data

#######################################################################

#########
# Login #
#########

username = app_data.username()

##########
# Charts #
##########

# Tanzmusik Online data range
tmo_base_from_year = 2018
tmo_base_from_week = 30
tmo_base_to_year = 2018
tmo_base_to_week = 30
tmo_new_from_year = 2018
tmo_new_from_week = 29
tmo_new_to_year = 2018
tmo_new_to_week = 29

#######
# GUI #
#######

gui_border_x = 2
gui_border_y = 2

gui_left_begin_x = gui_border_x
gui_left_label_width = 13
gui_left_data_width = 60
gui_left_heading_y = gui_border_y
gui_left_artist_y = gui_left_heading_y + 1
gui_left_songtitle_y = gui_left_artist_y + 1
gui_left_dance_style_y = gui_left_songtitle_y + 1

gui_left_right_separation = 7

gui_right_begin_x = gui_left_begin_x + gui_left_label_width + gui_left_data_width + gui_left_right_separation
gui_right_label_width = 15
gui_right_data_width = 60
gui_right_heading_y = gui_border_y
gui_right_artist_y = gui_right_heading_y + 1
gui_right_songtitle_y = gui_right_artist_y + 1
gui_right_tpm_y = gui_right_songtitle_y + 1
gui_right_target_playlist_y = gui_right_tpm_y + 1

#######################################################################

default_config = {
    'tmo_base_from_year': tmo_base_from_year,
    'tmo_base_from_week': tmo_base_from_week,
    'tmo_base_to_year': tmo_base_to_year,
    'tmo_base_to_week': tmo_base_to_week,
    'tmo_new_from_year': tmo_new_from_year,
    'tmo_new_from_week': tmo_new_from_week,
    'tmo_new_to_year': tmo_new_to_year,
    'tmo_new_to_week': tmo_new_to_week,
    'gui_border_x': gui_border_x,
    'gui_border_y': gui_border_y,
    'gui_left_begin_x': gui_left_begin_x,
    'gui_left_label_width': gui_left_label_width,
    'gui_left_data_width': gui_left_data_width,
    'gui_left_heading_y': gui_left_heading_y,
    'gui_left_artist_y': gui_left_artist_y,
    'gui_left_songtitle_y': gui_left_songtitle_y,
    'gui_left_dance_style_y': gui_left_dance_style_y,
    'gui_left_right_separation': gui_left_right_separation,
    'gui_right_begin_x': gui_right_begin_x,
    'gui_right_label_width': gui_right_label_width,
    'gui_right_data_width': gui_right_data_width,
    'gui_right_heading_y': gui_right_heading_y,
    'gui_right_artist_y': gui_right_artist_y,
    'gui_right_songtitle_y': gui_right_songtitle_y,
    'gui_right_tpm_y': gui_right_tpm_y,
    'gui_right_target_playlist_y': gui_right_target_playlist_y
}


# https://stackoverflow.com/questions/3387691/how-to-perfectly-override-a-dict
class ConfigDict(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    # This implementation first tries to get the value of a missing key from
    # the default configuration before raising a KeyError
    def __getitem__(self, key):
        result = None
        try:
            result = self.store[key]
        except KeyError:
            logging.warning("ConfigDict: key '{}' not found, trying to get value from default config.".format(key))
            self.store[key] = default_config[key]
            result = self.store[key]
            logging.warning("ConfigDict: '{}' default: {}".format(key, str(result)))
        return result

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
    
    def to_dict(self):
        return self.store

def get_config(path = './settings.cfg'):
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                config = ConfigDict(yaml.load(f))
                logging.debug("get_config: restored saved config from '{}'".format(path))
                return config
            except yaml.YAMLError as e:
                logging.warning('get_config: yaml.load encountered a decoding error:')
                logging.warning(str(e))
                logging.warning('get_config: Loading defaults.')
    else:
        logging.warning("get_config: settings file didn't exist at path '{}'. Loading defaults.".format(path))

    return ConfigDict(default_config)

def save_config(config, path = './settings.cfg'):
    try:
        with open(path, 'w') as f:
            yaml.dump(config.to_dict(), f, default_flow_style = False)
            logging.debug("save_config: wrote current config to '{}'".format(path))
    except Exception as e:
        logging.warning("save_config: caught exception. Couldn't write to file '{}'".format(path))
        logging.warning(str(e))
