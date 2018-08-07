import tmo_processing
import sys
from asciimatics.screen import Screen
from time import sleep
from trimmable_string import TrimmableString
from spotipy_interface import sp_login, sp_find, sp_play, sp_pause_resume, sp_skip, sp_seek, sp_add
import tap_tempo
import yaml
import math
import logging

def sleep_ms(t):
    sleep(t/1000)

# Earliest: 2008-20
base_from_year = 2018
base_from_week = 30
base_to_year = 2018
base_to_week = 30

new_from_year = 2018
new_from_week = 29
new_to_year = 2018
new_to_week = 29

border_x = 2
dataset_width_tmo = 60
dataset_y = 2
heading_y = dataset_y + 0
heading_width_tmo = 13
heading_width_spotify = 15
artist_y = dataset_y + 2
title_y = artist_y + 1
dance_style_y = title_y + 1
tpm_y = title_y + 1
target_playlist_y = tpm_y + 1
arrow_width = 7
spotify_x = border_x + heading_width_tmo + dataset_width_tmo + arrow_width

with open('dance_style_mapping.yaml', 'r') as f:
    tmo_spotify_dance_style_mapping = yaml.load(f)

with open('spotify_playlist_export.yaml', 'r') as f:
    spotify_playlist_mapping = yaml.load(f)

new_songs = tmo_processing.get_charts_difference(base_from_year, 
                                                 base_from_week, 
                                                 base_to_year, 
                                                 base_to_week, 
                                                 new_from_year, 
                                                 new_from_week, 
                                                 new_to_year, 
                                                 new_to_week,
                                                 sort_by='artist')
tmo_n_items = len(new_songs)

def get_key_blocking(screen):
    no_input = True
    while no_input:
        key_code = screen.get_key()
        if key_code is not None:
            no_input = False
        sleep_ms(1)
    return key_code


def init_tpm():
    return tap_tempo.TPMTapper()


def update_tpm(screen, tpm):
    screen.print_at('{}'.format(tpm.get_n_taps().rjust(3, ' ')), screen.width - 5, 0)
    screen.print_at('TPM[{}/4]: {}     '.format(tpm.get_beats_per_bar(), tpm.get_tpm().rjust(10, ' ')), screen.width - 20, 1)


def tpm_screen(screen, tpm):
    while True:
        draw_tpm(screen, tpm, bg = Screen.COLOUR_BLUE)
        screen.refresh()

        key_code = get_key_blocking(screen)
        if key_code == Screen.KEY_ESCAPE:
            return
        if key_code in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')):
            tpm.set_beats_per_bar(key_code - ord('1') + 1)
        else:
            tpm.tap()

def draw_tmo_dataset(screen, tmo_item_index, tmo_n_items, tmo_artist, tmo_title, tmo_dance_style):
    draw_tmo_headings(screen, tmo_item_index, tmo_n_items)
    draw_tmo_artist(screen, tmo_artist)
    draw_tmo_title(screen, tmo_title)
    draw_tmo_dance_style(screen, tmo_dance_style)


def draw_tmo_headings(screen, tmo_item_index, tmo_n_items):
    screen.print_at('--- TM Online [{}/{}] ---'.format(tmo_item_index, tmo_n_items), border_x, heading_y)
    screen.print_at('Artist:', border_x, artist_y)
    screen.print_at('Title:', border_x, title_y)
    screen.print_at('Dance Style:', border_x, dance_style_y)


def draw_tmo_artist(screen, tmo_artist, bg = 0):
    s = '{{:{}}}'.format(dataset_width_tmo)
    screen.print_at(s.format(str(tmo_artist)), border_x + heading_width_tmo, artist_y, bg = bg)


def draw_tmo_title(screen, tmo_title, bg = 0):
    s = '{{:{}}}'.format(dataset_width_tmo)
    screen.print_at(s.format(str(tmo_title)), border_x + heading_width_tmo, title_y, bg = bg)


def draw_tmo_dance_style(screen, tmo_dance_style, bg = 0):
    s = '{{:{}}}'.format(dataset_width_tmo)
    screen.print_at(s.format(str(tmo_dance_style)), border_x + heading_width_tmo, dance_style_y, bg = bg)


def draw_mapping_arrow(screen):
    screen.print_at('===>>', border_x + dataset_width_tmo + heading_width_tmo + 1, heading_y + 1)



def draw_spotify_dataset(screen, spotify_item_index, spotify_n_items, spotify_current_song, spotify_target_playlist, tpm):

    if spotify_current_song is None:
        draw_spotify_headings(screen, 0, 0, tpm)
        draw_spotify_artist(screen, '')
        draw_spotify_title(screen, '')
        draw_tpm(screen, tpm)
        draw_spotify_target_playlist(screen, '')
    else:
        draw_spotify_headings(screen, spotify_item_index, spotify_n_items, tpm)
        title = spotify_current_song['name']
        artist = spotify_current_song['artists'][0]['name']
        draw_spotify_artist(screen, artist)
        draw_spotify_title(screen, title)
        draw_tpm(screen, tpm)
        if spotify_target_playlist is not None:
            draw_spotify_target_playlist(screen, spotify_target_playlist)
        else:
            draw_spotify_target_playlist(screen, 'missing TPM')


def draw_spotify_headings(screen, spotify_item_index, spotify_n_items, tpm):
    screen.print_at('--- SPOTIFY [{}/{}] ---'.format(spotify_item_index, spotify_n_items), spotify_x, heading_y)
    screen.print_at('Artist:', spotify_x, artist_y)
    screen.print_at('Title:', spotify_x, title_y)
    screen.print_at('--> Playlist:', spotify_x, target_playlist_y)


def draw_spotify_artist(screen, artist, bg = 0):
    s = '{{:{}}}'.format(dataset_width_tmo)
    screen.print_at(s.format(str(artist)), spotify_x + heading_width_spotify, artist_y, bg = bg)


def draw_spotify_title(screen, title, bg = 0):
    s = '{{:{}}}'.format(dataset_width_tmo)
    screen.print_at(s.format(str(title)), spotify_x + heading_width_spotify, title_y, bg = bg)


def draw_tpm(screen, tpm, bg = 0):
    screen.print_at('TPM [{}/4]:'.format(tpm.get_beats_per_bar()), spotify_x, tpm_y)
    screen.print_at('{}     '.format(tpm.get_tpm().rjust(10, ' ')), spotify_x + heading_width_spotify, tpm_y, bg = bg)


def draw_spotify_target_playlist(screen, target_playlist, bg = 0):
    s = '{{:{}}}'.format(dataset_width_tmo)
    screen.print_at(s.format(str(target_playlist)), spotify_x + heading_width_spotify, target_playlist_y, bg = bg)


def draw_error(screen, msg):
    error_x = math.floor(screen.width / 2) - 40
    error_y = math.floor(screen.height / 2) + 3
    if msg == '':
        screen.print_at('{}'.format(msg).ljust(40, ' '), error_x, error_y)
    else:
        screen.print_at('{}'.format(msg).ljust(40, ' '), error_x, error_y, bg = Screen.COLOUR_RED)


def get_target_playlist_obj(spotify_current_song, tpm, tmo_dance_style):
    target_playlist_obj = None
    if spotify_current_song is not None and tpm.valid_tpm():
        target_playlist_obj = spotify_playlist_mapping.get(tmo_spotify_dance_style_mapping.get(str(tmo_dance_style), None), {}).get(math.floor(float(tpm.get_tpm())), None)

    return target_playlist_obj


def get_target_playlist_name(spotify_current_song, tpm, tmo_dance_style):
    target_playlist_name = ''
    target_playlist_obj = get_target_playlist_obj(spotify_current_song, tpm, tmo_dance_style)
    if target_playlist_obj is not None:
        target_playlist_name = target_playlist_obj['name']

    return target_playlist_name


def draw_data_once(screen, tmo_item_offset, tmo_n_items, tmo_artist, tmo_title, tmo_dance_style, spotify_items_offset, spotify_n_items, spotify_current_song, target_playlist_name, tpm):
    draw_tmo_dataset(screen, tmo_item_offset + 1, tmo_n_items, tmo_artist, tmo_title, tmo_dance_style)
    draw_spotify_dataset(screen, spotify_items_offset + 1, spotify_n_items, spotify_current_song, target_playlist_name, tpm)



def main_screen(screen):
    for tmo_item_offset, song in enumerate(new_songs):
        tmo_dance_style = song[2]
        tmo_artist = TrimmableString(song[0])
        tmo_title = TrimmableString(song[1])

        spotify_current_song = None
        spotify_n_items = 0
        spotify_items_offset = 0
        items = sp_find(tmo_artist, tmo_title)
        if items is not None:
            spotify_n_items = len(items)
            spotify_current_song = items[spotify_items_offset]
        tpm = init_tpm()

        error_text = ''
        goto_next_song = False
        while not goto_next_song:
            screen.clear()

            target_playlist_name = get_target_playlist_name(spotify_current_song, tpm, tmo_dance_style)
            draw_data_once(screen, tmo_item_offset, tmo_n_items, tmo_artist, tmo_title, tmo_dance_style, spotify_items_offset, spotify_n_items, spotify_current_song, target_playlist_name, tpm)

            screen.print_at('{:10}{:10}{:10}{:10}{:10}{:10}{:10}{:10} '.format('(a)dd', '(q)uit', '(s)kip', '(p)lay', '(i) prev', '(o) next', '(u) pause', '(t)ap'), 0, screen.height - 2)
            screen.print_at('{:10}{:10}{:10}{:10} '.format('(j) artist -word', '(k) artist -char', '(l) title -word', '(m) title -char'), 0, screen.height - 1)
            
            draw_error(screen, error_text)

            screen.refresh()
            
            key_code = get_key_blocking(screen)
            
            error_text = ''
            if key_code in (ord('A'), ord('a')):
                if spotify_current_song is None:
                    error_text = 'ERROR: Find suitable song first!'
                elif not tpm.valid_tpm():
                    error_text = 'ERROR: Tap tempo first!'
                elif target_playlist_name == '':
                    error_text = 'ERROR: no suitable playlist'
                else:
                    sp_add(spotify_current_song, get_target_playlist_obj(spotify_current_song, tpm, tmo_dance_style))

                    

            if key_code in (ord('Q'), ord('q')):
                return # quit
            if key_code in (ord('S'), ord('s')):
                goto_next_song = True

            if key_code in (ord('F'), ord('f')):
                items = sp_find(tmo_artist, tmo_title)
                if items is not None:
                    spotify_n_items = len(items)
                    spotify_items_offset = 0
                    spotify_current_song = items[spotify_items_offset]
                else:
                    spotify_current_song = None
            if key_code in (ord('P'), ord('p')):
                if spotify_current_song is not None:
                    sp_play(items, spotify_items_offset)
            if key_code == ord('i'):
                if spotify_items_offset != 0:
                    sp_skip(-1)
                    spotify_items_offset -= 1
            if key_code == ord('I'):
                sp_seek(-1)
            if key_code == ord('o'):
                if spotify_items_offset != spotify_n_items - 1:
                    sp_skip(1)
                    spotify_items_offset += 1
            if key_code == ord('O'):
                sp_seek(1)
            if key_code in (ord('U'), ord('u')):
                sp_pause_resume()

            if key_code in (ord('T'), ord('t')):
                screen.print_at('TAPPING', screen.width - 20, 0)
                tpm_screen(screen, tpm)

            if key_code == ord('j'):
                tmo_artist.remove_word()
            if key_code == ord('k'):
                tmo_artist.remove_char()
            if key_code == ord('l'):
                tmo_title.remove_word()
            if key_code == ord('m'):
                tmo_title.remove_char()
            if key_code == ord('J'):
                tmo_artist.reveal_word()
            if key_code == ord('K'):
                tmo_artist.reveal_char()
            if key_code == ord('L'):
                tmo_title.reveal_word()
            if key_code in (ord('é'), ord('ö'), ord('Ö')):
                tmo_title.reveal_char()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    sp_login()
    Screen.wrapper(main_screen)


