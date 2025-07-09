import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from spotify_tracks import get_playlist_tracks
import time

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated():
    """Authenticate Google user and return YouTube client."""
    try:
        creds_file = 'creds.json'
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        credentials = flow.run_local_server(port=0)
        youtube = build('youtube', 'v3', credentials=credentials)
        return youtube
    except Exception as e:
        print(f"Error in get_authenticated: {e}")
        return None

def create_playlist(youtube, title, description='', privacy_status='private'):
    """Create YouTube playlist and return its ID."""
    try:
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
    except Exception as e:
        print(f"Error in create_playlist: {e}")
        return None

def add_music_to_playlist(youtube, playlist_id, video_id):
    """Add video to YouTube playlist."""
    try:
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
        print(f"Added: {video_id}")
        return response
    except Exception as e:
        print(f"Error in add_music_to_playlist: {e}")
        return None

def extract_video_id_yt(url):
    """Extract video id from YouTube link."""
    try:
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        return query.get('v',[None])[0]
    except Exception as e:
        print(f"Error in extract_video_id_yt: {e}")
        return None

def extract_playlist_id_spotify(url):
    """Extract Spotify playlist id from its link."""
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        playlist_index = path_parts.index('playlist')
        return path_parts[playlist_index + 1]
    except Exception as e:
        print(f"Error in extract_playlist_id_spotify: {e}")
        return None

def search_youtube_video(youtube_client, title, author):
    """Search YouTube for a video, extract its video ID."""
    try:
        query = f"{title} {author}"
        request = youtube_client.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            print(f"No video found for {title} - {author}")
            return None
        return items[0]["id"]["videoId"]
    except Exception as e:
        print(f"Error in search_youtube_video: {e}")
        return None

if __name__ == '__main__':
    youtube_client = get_authenticated()
    if not youtube_client:
        print("YouTube authentication failed. Exiting.")
        exit(1)
    print('YouTube authentication successful.')

    # Playlist details input
    playlist_title = input("Enter playlist's title: ")
    playlist_description = input("Enter description: ")
    valid_privacy = ['public', 'unlisted', 'private']

    while True:
        playlist_privacy = input("Enter privacy status (public, unlisted, private): ").strip().lower()
        if playlist_privacy in valid_privacy:
            break
        print("Invalid privacy, please choose from: public, unlisted, private.")

    # Create new YouTube playlist
    new_playlist_id = create_playlist(youtube_client, playlist_title, playlist_description, playlist_privacy)
    if not new_playlist_id:
        print("Failed to create playlist. Exiting.")
        exit(1)
    print(f"Playlist created: https://www.youtube.com/playlist?list={new_playlist_id}")

    # Spotify playlist URL input with validation
    while True:
        playlist_url = input("Provide Spotify playlist URL: ")
        playlist_id = extract_playlist_id_spotify(playlist_url)
        if playlist_id:
            break
        print("Invalid Spotify playlist URL. Please try again.")

    # Fetch tracks from Spotify playlist
    spotify_playlist_tracks = get_playlist_tracks(playlist_id)
    print(f"Found {len(spotify_playlist_tracks)} tracks.")

    # Loop through Spotify playlist and append to YouTube playlist
    for track in spotify_playlist_tracks:
        try:
            video_id = search_youtube_video(youtube_client, track['title'], track['author'])
            if not video_id:
                print(f"No video found for {track['title']} - {track['author']}")
                continue
            add_music_to_playlist(youtube_client, new_playlist_id, video_id)
            time.sleep(1)
        except Exception as e:
            print(f"Error processing {track['title']} - {track['author']}: {e}")

    print(f"Playlist: https://www.youtube.com/playlist?list={new_playlist_id}")