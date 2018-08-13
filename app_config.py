import sys
import os
import json
import logging

#######################################################################

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


def get_config(path = './settings.cfg'):
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                config = json.load(f)
                logging.debug("get_config: restored saved config from '{}'".format(path))
                return config
            except json.JSONDecodeError as e:
                logging.warning('get_config: JSON.load encountered a decoding error:')
                logging.warning(str(e))
                logging.warning('get_config: Loading defaults.')
    else:
        logging.warning("get_config: settings file didn't exist at path '{}'. Loading defaults.".format(path))

    return default_config

def save_config(config, path = './settings.cfg'):
    try:
        with open(path, 'w') as f:
            json.dump(config, f)
            logging.debug("save_config: wrote current config to '{}'".format(path))
    except Exception as e:
        logging.warning("save_config: caught exception. Couldn't write to file '{}'".format(path))
        logging.warning(str(e))
