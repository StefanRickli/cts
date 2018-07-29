import numpy as np
from bs4 import BeautifulSoup
from tanzmusik_online_get_charts import get_chartnumbers
import time
from pathlib import Path
import pickle
import console_utils
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
base_path = 'chart_html/'


def get_song_title(song_div):
    title_link = song_div.find('div', {'class': 'songTitle'}).find('a')
    return title_link.string


def get_song_artist(song_div):
    artist_link = song_div.find('span', {'class': 'artist'}).find('a')
    return artist_link.string


def get_song_dancestyle(song_div):
    dancestyle_link = song_div.find('div', {'class': 'dances'}).find('a')
    return dancestyle_link.string


def get_song_url(song_div):
    title_link = song_div.find('div', {'class': 'songTitle'}).find('a')
    return title_link['href']


def scrape_file(filename):
    if Path('{}.set.pkl'.format(filename)).exists():
        with open('{}.set.pkl'.format(filename), 'rb') as f_restore:
            return pickle.load(f_restore)

    with open('{}.html'.format(filename), 'rb') as f_raw:
        soup = BeautifulSoup(f_raw, 'html.parser')
        song_set = set()
        for div in soup.select("div[class='song']"):
            title = str(get_song_title(div))
            artist = str(get_song_artist(div))
            dancestyle = str(get_song_dancestyle(div))
            url = str(get_song_url(div))

            song_set.add((artist, title, dancestyle, url))

        with open('{}.set.pkl'.format(filename), 'wb') as f_save:
            pickle.dump(song_set, f_save)
        return song_set


def compile_set(from_year, from_week, to_year, to_week):
    chartnumbers = get_chartnumbers(from_year, from_week, to_year, to_week)
    compilation = set()

    ts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ind = 0
    n_items = len(chartnumbers)
    for i, chartnumber in enumerate(chartnumbers):
        filename = '{}{}'.format(base_path, chartnumber)
        try:
            tic = time.time()
            song_set = scrape_file(filename)
            compilation.update(song_set)
            ts[ind] = time.time() - tic
            if ts[ind] > 0.01 or (i % 10) == 0:
                ind = (ind + 1) % 5
                n_items_left = n_items - i - 1
                time_left = n_items_left * sum(ts) / min(i + 1, 10)
                logging.debug('{:03}/{:03}: Added {} to set. ~{:.0f}s left.'.format(i + 1, n_items, chartnumber, time_left))
        except:
            pass

    return compilation


def chart_difference(base_from_year, base_from_week, base_to_year, base_to_week, compare_from_year, compare_from_week, compare_to_year, compare_to_week):
    logging.debug('Preparing base set.')
    base_set = compile_set(base_from_year, base_from_week, base_to_year, base_to_week)
    if not base_set:
        logging.debug('Base set is empty.')

    logging.debug('Preparing comparison set.')
    compare_set = compile_set(compare_from_year, compare_from_week, compare_to_year, compare_to_week)
    if not compare_set:
        logging.debug('Comparison set is empty.')

    # Remove all elements from the comparison-set that have already been seen in the base-set
    result = compare_set - base_set
    
    logging.info('Set comparison revealed {} new songs in total.'.format(len(result)))
    return result


def get_charts_difference(base_from_year, base_from_week, base_to_year, base_to_week, compare_from_year, compare_from_week, compare_to_year, compare_to_week, sort_by='artist'):
    
    new_songs = list(chart_difference(base_from_year, base_from_week, base_to_year, base_to_week, compare_from_year, compare_from_week, compare_to_year, compare_to_week))

    if sort_by == 'artist':
        return sorted(new_songs, key=lambda x : x[0])

    if sort_by == 'title':
        return sorted(new_songs, key=lambda x : x[1])

    if sort_by == 'dance_style':
        return sorted(new_songs, key=lambda x : x[2])

    logging.debug('Done.')


def write_result(result):
    with open('new_songs.txt', 'w', encoding='utf-8') as f:
        f.write('Comparing the song charts in the period ({}-{}/{}-{}) to the song charts in the period ({}-{}/{}-{}) reveals the following new, unseen songs:'.format(base_from_year, base_from_week, base_to_year, base_to_week, compare_from_year, compare_from_week, compare_to_year, compare_to_week))
        for i, song in enumerate(new_songs_by_artist):
            f.write('{:04}: {:50}{:60}{:20}{}\n'.format(i, song[0], song[1], song[2], song[3]))

    with open('new_songs.csv', 'w', encoding='utf-8') as f:
        f.write('Artist\tTitle\tDance Style\tURL\n')
        for i, song in enumerate(new_songs_by_artist):
            f.write('{}\t{}\t{}\t{}\n'.format(song[0], song[1], song[2], song[3]))

    logging.info('Wrote result to files.')
    return result


if __name__ == '__main__':
    base_from_year = 2008
    base_from_week = 20
    base_to_year = 2010
    base_to_week = 53

    compare_from_year = 2011
    compare_from_week = 1
    compare_to_year = 2018
    compare_to_week = 30

    new_songs_by_artist = get_charts_difference(base_from_year, base_from_week, base_to_year, base_to_week, compare_from_year, compare_from_week, compare_to_year, compare_to_week)
    
    write_result(new_songs_by_artist)


