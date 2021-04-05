import spotipy
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
import spotipy.util as util
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

# This function involves the security of spotipy and reads the login information
def security():
    f = open("config.txt", "r")
    user = f.readline()[:-1]
    pwd = f.readline()

    # client_manager = SpotifyClientCredentials(client_id=user,client_secret=pwd)
    # token = client_manager.get_access_token()
    scope = "user-read-private playlist-modify-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=user,
                                                   client_secret=pwd,
                                                   redirect_uri="http://localhost:8888/callback"))
    return sp

# Given a playlist of songs, this function gets each song's ID
def get_songs(playlist_id):
    sp = security()
    playlist = sp.playlist_items(playlist_id)
    songs_from_playlist = []
    for song in playlist["items"]:
        songs_from_playlist.append(song["track"]["id"])
    return songs_from_playlist


# ranges: lower and upper bounds (list of 2 numbers)
# dataset: string containing path to file containing data
# songlist: array of strings of song id's
# This function takes the given songs (it will only use songs that are in the 175k+ song database)
# and returns a list of songs
def better_recs(ranges, dataset, songlist):
    df_b = pd.read_csv(dataset, chunksize=10000)
    # Create the dataframe for the business dataset
    curr = None
    for chunk in df_b:
        temp = chunk
        if curr is None and len(temp.index) > 0:
            curr = temp
        elif len(temp.index) > 0:
            curr = curr.append(temp)
    # curr.loc[curr["acousticness"] > 0.5,"acousticness"] *= 100
    # curr.loc[curr["acousticness"] < 0.5,"acousticness"] *= 1000
    curr.loc[:, "loudness"] += 60
    curr.loc[:, "loudness"] /= 64
    curr.loc[:, "popularity"] /= 100
    curr.loc[:, "tempo"] /= 244
    curr.loc[:, "year"] -= 1920
    curr.loc[:, "year"] /= 101
    curr = curr.loc[:,
           ["acousticness", "danceability", "energy", "instrumentalness","liveness", "loudness", "popularity",
            "speechiness", "tempo", "year", "id"]]

    currlist = np.array(curr.values.tolist())
    attributes = currlist[:, :-1]
    song_id = currlist[:, -1]

    test = attributes[np.isin(song_id, songlist), :]
    point_avg = np.mean(test.astype(np.float64), axis=0)
    point_avg = point_avg.reshape(1, -1)

    neigh = NearestNeighbors(n_neighbors=ranges[1])
    neigh.fit(attributes)
    dist, index = neigh.kneighbors(point_avg)
    index = index[:, ranges[0]:ranges[1]]
    recommended_songs = song_id[index[0]]
    curr.to_csv("modified.csv")
    return recommended_songs

# This function takes the list of songs and turns it into a playlist
# and adds it to the user's Spotify account.
def make_playlist(list_id,playlist_name):
    sp = security()
    # sp = spotipy.Spotify(auth=token)
    curr_user = sp.me()["id"]
    new_playlist = sp.user_playlist_create(curr_user, playlist_name, public=False, collaborative=False,
                                           description="")
    sp.playlist_add_items(new_playlist["id"], list_id, position=None)