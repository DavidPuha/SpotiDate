import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

def main():
    client_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    client_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

    # API connection
    API = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_ID,
            client_secret=client_SECRET,
            redirect_uri="http://localhost:3000",
            scope="user-read-private playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public",
        )
    )
    
    userID = API.current_user().get("id") # currently logged in userID
    playlists = [] # ARR with all playlists

    offset = 0
    while True:
        data = API.user_playlists(userID, offset=offset).get("items") # GET all the playlists available for the user and filter them
        if len(data) == 0:
            break
        for res in data: 
            playlists.append({"name": res["name"], "id": res["id"]})
        offset += 50

    print("-------------------------------------------")
    print("COPY from Playlist:")
    for i, item in enumerate(playlists):
        print(f"{i}) {item["name"]}")
    
    user_input = ""
    while user_input not in map(str, range(0, len(playlists))):
        user_input = input("Your choice: ")

    songs_to_copy = findSongs(API, playlists[int(user_input)].get("id"))

    playlists.insert(0, {"name": "Create Playlist", "id": "Create Playlist"}) # INSERT a new item so you can create a New Playlist by choosing the option

    print("-------------------------------------------")
    print("COPY to Playlist:")
    for i, item in enumerate(playlists):
        print(f"{i}) {item["name"]}")
    
    user_input = ""
    while user_input not in map(str, range(0, len(playlists))):
        user_input = input("Your choice: ")
    
    create_new_playlist = bool(int(user_input) == 0)
    playlist_ID = playlists[int(user_input)].get("id")

    if (create_new_playlist == True):
        playlist_name = input("Playlist Name: ")

        playlist_private = ""
        while playlist_private not in map(str, ["1", "0"]):
            playlist_private = input("Private Playlist? 0 - False / 1 - True: ")
        
        playlist_private = bool(int(playlist_private) == 1)

        # True is actually False on Spotify's end for private playlist...
        playlist_ID = API.user_playlist_create(userID, playlist_name, not playlist_private).get("id")
    else:
        songs_to_filter = findSongs(API, playlist_ID)
        songs_to_copy = [x for x in songs_to_copy if x not in songs_to_filter]

    for data in songs_to_copy:
        API.playlist_add_items(playlist_ID, [data])
        time.sleep(1)

def findSongs(API, playlistID):
    # GET all Songs found in a playlist
    offset = 0
    all_songs = []
    while True:
        data = API.playlist_items(playlistID, limit=100 , offset=offset).get("items")
        print(f"Retrieved {offset} songs!")
        if len(data) == 0:
            break
        all_songs.extend(data)
        offset += 100

    # FILTER all songs to just their trackID
    songs_to_copy = []
    for item in all_songs:
        if (item["is_local"] == True):
            continue
        trackID = item["track"]["id"]
        songs_to_copy.append(trackID)

    return songs_to_copy

if __name__ == "__main__":
    main()
