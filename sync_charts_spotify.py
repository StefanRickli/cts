import tmo_processing
import sys
from asciimatics.screen import Screen
from time import sleep
from trimmable_string import TrimmableString
from spotipy_interface import sp_login, sp_find, sp_play, sp_pause_resume, sp_skip, sp_seek
import tap_tempo

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

new_songs = tmo_processing.get_charts_difference(base_from_year, 
                                                 base_from_week, 
                                                 base_to_year, 
                                                 base_to_week, 
                                                 new_from_year, 
                                                 new_from_week, 
                                                 new_to_year, 
                                                 new_to_week,
                                                 sort_by='artist')


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
        update_tpm(screen, tpm)
        screen.refresh()

        key_code = get_key_blocking(screen)
        if key_code == Screen.KEY_ESCAPE:
            return
        if key_code in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9')):
            tpm.set_beats_per_bar(key_code - ord('1') + 1)
        else:
            tpm.tap()




def main_screen(screen):
    for song in new_songs:
        song_dance_style = song[2]
        song_artist = TrimmableString(song[0])
        song_title = TrimmableString(song[1])

        song_found = False
        items_offset = 0
        items = sp_find(song_artist, song_title)
        if items is not None:
            n_items = len(items)
            sp_song_title = items[items_offset]['name']
            sp_song_artist = items[items_offset]['artists'][0]['name']
            song_found = True
        tpm = init_tpm()

        goto_next_song = False
        while not goto_next_song:
            screen.clear()

            screen.print_at('[{}] {} - {}'.format(song_dance_style, song_artist, song_title), 0, 0)
            if song_found:
                screen.print_at('Spotify: {} - {} [{}/{}]'.format(sp_song_artist, sp_song_title, items_offset + 1, n_items), 0, 1)
            else:
                screen.print_at('Spotify: no results', 0, 1)

            update_tpm(screen, tpm)

            screen.print_at('{:10}{:10}{:10}{:10}{:10}{:10}{:10}{:10} '.format('(a)dd', '(q)uit', '(s)kip', '(p)lay', '(i) prev', '(o) next', '(u) pause', '(t)ap'), 0, 3)
            screen.print_at('{:10}{:10}{:10}{:10} '.format('(j) artist -word', '(k) artist -char', '(l) title -word', '(m) title -char'), 0, 4)
            
            screen.refresh()
            
            key_code = get_key_blocking(screen)
            
            if key_code in (ord('Q'), ord('q')):
                return # quit
            if key_code in (ord('S'), ord('s')):
                goto_next_song = True

            if key_code in (ord('F'), ord('f')):
                items = sp_find(song_artist, song_title)
                if items is not None:
                    n_items = len(items)
                    items_offset = 0
                    sp_song_title = items[items_offset]['name']
                    sp_song_artist = items[items_offset]['artists'][0]['name']
                    song_found = True
                else:
                    song_found = False
            if key_code in (ord('P'), ord('p')):
                if song_found:
                    sp_play(items, items_offset)
            if key_code == ord('i'):
                if items_offset != 0:
                    sp_skip(-1)
                    items_offset -= 1
            if key_code == ord('I'):
                sp_seek(-1)
            if key_code == ord('o'):
                if items_offset != n_items - 1:
                    sp_skip(1)
                    items_offset += 1
            if key_code == ord('O'):
                sp_seek(1)
            if key_code in (ord('U'), ord('u')):
                sp_pause_resume()

            if key_code in (ord('T'), ord('t')):
                screen.print_at('TAPPING', screen.width - 20, 0)
                tpm_screen(screen, tpm)

            if key_code == ord('j'):
                song_artist.remove_word()
            if key_code == ord('k'):
                song_artist.remove_char()
            if key_code == ord('l'):
                song_title.remove_word()
            if key_code == ord('m'):
                song_title.remove_char()
            if key_code == ord('J'):
                song_artist.reveal_word()
            if key_code == ord('K'):
                song_artist.reveal_char()
            if key_code == ord('L'):
                song_title.reveal_word()
            if key_code in (ord('é'), ord('ö'), ord('Ö')):
                song_title.reveal_char()

sp_login()
Screen.wrapper(main_screen)

if __name__ == '__main__':
    pass    


        
