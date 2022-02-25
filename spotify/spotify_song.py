from spotipy import Spotify, SpotifyClientCredentials
from requests import get
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class SpotifySongFinder:
    def __init__(self):
        """class that finds the top song on a given date through web scraping and finds that song in spotify
        using the spotify API"""

        self.cid = getenv('SPOTIFY_CID')
        self.secret = getenv('SPOTIFY_SECRET')
        self.auth_manager = SpotifyClientCredentials(
            client_id=self.cid, client_secret=self.secret)
        self.sp = Spotify(auth_manager=self.auth_manager)
        self.songs = ''

    def scrape_top_song(self, date):
        """takes a string input of date YYYY-MM-DD and finds the billboard top 100 number 1
        on that date, returning the song name and artist as strings"""

        response = get(
            f'https://www.billboard.com/charts/hot-100/{date}/')

        website_html = response.text

        soup = BeautifulSoup(website_html, 'html.parser')

        soup_data = soup.find_all(
            name='li', class_='o-chart-results-list__item', limit=4)

        soup_song = soup_data[3]

        song = soup_song.find(name='h3', class_='c-title',
                              id="title-of-a-story").string.strip('\n')
        artist = soup_song.find(
            name='span', class_='c-label').string.strip('\n')

        return song, artist

    def find_song_uri(self, song, artist):
        """takes a string inputs for a song and artist and returns the spotify uri code
        for that song as a string"""

        result = self.sp.search(
            q=f'artist:{artist}%20track:{song}', type='track')
        try:
            uri = result['tracks']['items'][0]['uri']
            url = result['tracks']['items'][0]['external_urls']['spotify']
        except IndexError:
            result = self.sp.search(q=f'track:{song}', type='track')
            try:
                uri = result['tracks']['items'][0]['uri']
                url = result['tracks']['items'][0]['external_urls']['spotify']
            except IndexError:
                print('song not found')
        uri_code = uri.split(':')[2]
        return uri_code

    def get_top_song_info(self, date):
        """takes a string input as date YYYY-MM-DD and finds information on the billboard top 100 number 1 on that date
        returns a dictionary of strings with keys ''link'-the spotify link to the song, 'artist'-the artist, 'song'-the song,
        'date'-YYYY-MM-DD """

        song, artist = self.scrape_top_song(date)
        uri_code = self.find_song_uri(song, artist)
        link = f'https://open.spotify.com/track/{uri_code}'
        return {'link': link, 'artist': artist, 'song': song, 'date': date}
