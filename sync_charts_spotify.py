import tmo_processing
import sys
from asciimatics.screen import Screen
from time import sleep
from trimmable_string import TrimmableString
from spotipy_interface import sp_login, sp_find, sp_play, sp_pause_resume, sp_skip, sp_seek

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
        ev = screen.get_key()
        if ev is not None:
            no_input = False
        sleep_ms(1)
    return ev


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
        
        goto_next_song = False
        while not goto_next_song:
            screen.clear()

            screen.print_at('[{}] {} - {}'.format(song_dance_style, song_artist, song_title), 0, 0)
            if song_found:
                screen.print_at('Spotify: {} - {} [{}/{}]'.format(sp_song_artist, sp_song_title, items_offset + 1, n_items), 0, 1)
            else:
                screen.print_at('Spotify: no results', 0, 1)

            screen.print_at('\r{:10}{:10}{:10}{:10}{:10}{:10}{:10} '.format('(q)uit', '(s)kip', '(p)lay', '(i) prev', '(o) next', '(u) pause', '(t)ap'), 0, 3)
            screen.print_at('\r{:10}{:10}{:10}{:10} '.format('(j) artist -word', '(k) artist -char', '(l) title -word', '(m) title -char'), 0, 4)
            
            screen.refresh()
            
            ev = get_key_blocking(screen)
            
            if ev in (ord('Q'), ord('q')):
                return # quit
            if ev in (ord('S'), ord('s')):
                goto_next_song = True

            if ev in (ord('F'), ord('f')):
                items = sp_find(song_artist, song_title)
                if items is not None:
                    n_items = len(items)
                    items_offset = 0
                    sp_song_title = items[items_offset]['name']
                    sp_song_artist = items[items_offset]['artists'][0]['name']
                    song_found = True
                else:
                    song_found = False
            if ev in (ord('P'), ord('p')):
                if song_found:
                    sp_play(items, items_offset)
            if ev == ord('i'):
                if items_offset != 0:
                    sp_skip(-1)
                    items_offset -= 1
            if ev == ord('I'):
                sp_seek(-1)
            if ev == ord('o'):
                if items_offset != n_items - 1:
                    sp_skip(1)
                    items_offset += 1
            if ev == ord('O'):
                sp_seek(1)
            if ev in (ord('U'), ord('u')):
                sp_pause_resume()

            if ev in (ord('T'), ord('t')):
                pass
                #tap_screen(some_arg)

            if ev == ord('j'):
                song_artist.remove_word()
            if ev == ord('k'):
                song_artist.remove_char()
            if ev == ord('l'):
                song_title.remove_word()
            if ev == ord('m'):
                song_title.remove_char()
            if ev == ord('J'):
                song_artist.reveal_word()
            if ev == ord('K'):
                song_artist.reveal_char()
            if ev == ord('L'):
                song_title.reveal_word()
            if ev in (ord('é'), ord('ö'), ord('Ö')):
                song_title.reveal_char()

sp_login()
Screen.wrapper(main_screen)

if __name__ == '__main__':
    pass    




""" for song in new_songs:
    print()
    print('-' * 100)
    print()
    print('[{}] - {} by {}'.format(song[2], song[1], song[0]))
    
    goto_next_song = False
    while not goto_next_song:
        print('\r{:10}{:10}{:10}{:10}{:10}{:10}{:10} '.format('(q)uit', '(s)kip', '(p)lay', '(i) prev', '(o) next', '(u) stop', '(t)ap'), end='')
        choice = sys.stdin.readline()
        if choice == 'q\n':
            sys.exit()
        if choice == 's\n':
            goto_next_song = True
 """        

        
