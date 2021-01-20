import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests
import os

SPOTIFY_ID = os.environ.get('SPOTIFY_ID')
user_answer = input("which year you would like to travel to? Type the date in this format YYYY-MM-DD:  ")
response = requests.get(f"https://www.billboard.com/charts/hot-100/{user_answer}")
billboard_response = response.text
soup = BeautifulSoup(billboard_response, "html.parser")
rank = soup.find_all("span", class_="chart-element__rank__number")
songs = soup.find_all("span", class_="chart-element__information__song text--truncate color--primary")
artist = soup.find_all("span", class_="chart-element__information__artist text--truncate color--secondary")

top_100 = {}
for el in range(len(rank)):
    top_100[rank[el].getText()] = [songs[el].getText(), artist[el].getText()]

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=os.environ.get('SPOTIFY_ID'),
        client_secret=os.environ.get('SPOTIFY_SECRET'),
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
song_uris = []
year = user_answer.split("-")[0]

for song in songs:
    result = sp.search(q=f"track:{song.getText()} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song.getText()} doesn't exist in Spotify. Skipped.")


playlist = sp.user_playlist_create(user=user_id,
                                   name=f"{user_answer} Billboard 100",
                                   public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
