import yaml
import spotipy_interface
import spotipy
import re
import app_data

sp = spotipy_interface.get_authenticated_spotify()

# Get list of all playlists and assemble all paged results into one 'playlists' dict
playlists = []
response = sp.user_playlists(app_data.username())
while response:
    playlists.extend(response['items'])
    if response['next']:
        response = sp.next(response)
    else:
        response = None

# Create nested dict where the structure is as follows:
# Dance Style:
#   TPM:
#     Playlist Name
#     Playlist URI
#
# Access as follows:
# playlist_dict['Dance Style'][TPM]['name']
# playlist_dict['Dance Style'][TPM]['uri']
#
playlist_dict = {}
last_name = None
current_dance_style_playlists = {}
p = re.compile(r'([\d\D]*) (\d\d)-(\d\d)[\d\D]*')
for playlist in sorted(playlists, key = lambda x: x['name']):
    m = p.match(playlist['name'])
    if m:
        current_name = m.group(1)
        if current_name != last_name:
            if last_name is not None:
                playlist_dict[last_name] = current_dance_style_playlists
            current_dance_style_playlists = {}
            last_name = current_name

        for i in range(int(m.group(2)), int(m.group(3)) + 1):
            current_dance_style_playlists[i] = {'name': playlist['name'], 'uri': playlist['uri']}
playlist_dict[last_name] = current_dance_style_playlists

# Save assembled structure to a YAML-file
with open('spotify_playlist_export.yaml', 'w') as f:
    yaml.dump(playlist_dict, f, default_flow_style = False)
