import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

with open ('spotify_creds.json') as f:
    creds = json.load(f)
    client_id = creds['client_id']
    client_secret = creds['client_secret']

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_tracks(playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
        
    track_info = []
    #print(tracks)
    for i in tracks:
        title = i['track']['name']
        author = ", ".join([artist['name'] for artist in i['track']['artists']])
        
        track_info.append({"title": title, 'author': author})
        
    return track_info

