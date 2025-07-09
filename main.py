import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from spotify_tracks import get_playlist_tracks
import time

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated():
    creds_file = 'creds.json'
    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
    credentials = flow.run_local_server(port=0)
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

def create_playlist(youtube, title, description='', privacy_status='private'):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }
    )
    response = request.execute()
    return response['id']

def add_music_to_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet":{
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    response = request.execute()
    print(f"done")
    return response

def extract_video_id_yt(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    return query.get('v',[None])[0]

def extract_playlist_id_spotify(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    playlist_index = path_parts.index('playlist')
    return path_parts[playlist_index + 1]

def search_youtube_video(youtube_client, title, author):
    query = f"{title} {author}"
    request = youtube_client.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    items = response.get("items", [])
    return items[0]["id"]["videoId"]
   
    
if __name__ == '__main__':
    youtube_client = get_authenticated()
    print('DEBUG:works')
    
    playlist_title = "abcplaylist1"
    playlist_description = "checkcheck"
    playlist_privacy = 'private'
    
    new_playlist_id = create_playlist(youtube_client, playlist_title, playlist_description, playlist_privacy)
    print(f"Playlist created: https://www.youtube.com/playlist?list={new_playlist_id}")
    
    video_url = input("Paste url: ")
    playlist_url = input("Pasete spotify playlist url: ")
    
    video_url = extract_video_id_yt(video_url)
    playlist_url = extract_playlist_id_spotify(playlist_url)
    
    spotify_playlist_tracks = get_playlist_tracks(playlist_url)
    print(spotify_playlist_tracks)
    
    for track in spotify_playlist_tracks:
        video_id_unclean = search_youtube_video(youtube_client, track['title'], track['author'])
        #video_id_clean = extract_video_id_yt(video_id_unclean)
        add_music_to_playlist(youtube_client, new_playlist_id, video_id_unclean)
        time.sleep(1)
    
     