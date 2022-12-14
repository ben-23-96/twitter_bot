from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from requests import get
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv
from logger import EventLogger

load_dotenv()

log = EventLogger()


class SpotifySongFinder:
    def __init__(self):
        """class that finds the top song on a given date through web scraping and finds that song in spotify
        using the spotify API"""

        self.cid = getenv('SPOTIFY_CID')
        self.secret = getenv('SPOTIFY_SECRET')
        self.auth_manager = SpotifyClientCredentials(
            client_id=self.cid, client_secret=self.secret)
        self.sp = Spotify(client_credentials_manager=self.auth_manager)
        self.songs = ''

    def scrape_top_song(self, date):
        """takes a string input of date YYYY-MM-DD and finds the billboard top 100 number 1
        on that date, returning the song name and artist as strings"""

        log.add_log_entry(
            entry=f'scraping billboard for top song on date: {date}')

        response = get(
            f'https://www.billboard.com/charts/hot-100/{date}/')  # get website html

        website_html = response.text

        soup = BeautifulSoup(website_html, 'html.parser')

        soup_data = soup.find_all(
            name='li', class_='o-chart-results-list__item', limit=4)  # scrap page for top song
        try:
            soup_song = soup_data[3]
        except IndexError:
            log.add_log_entry(entry='no song found on page', is_error=True)
            return False

        song = soup_song.find(name='h3', class_='c-title',
                              id="title-of-a-story").string.strip('\n')
        artist = soup_song.find(
            name='span', class_='c-label').string.strip('\n')
        log.add_log_entry(
            entry=f'song found on billboard song: {song}, artist: {artist}')
        return {'song': song, 'artist': artist}

    def find_song_uri(self, song, artist):
        """takes a string inputs for a song and artist and returns the spotify uri code
        for that song as a string"""

        log.add_log_entry(entry='finding song uri code on spotify')
        result = self.sp.search(
            q=f'artist:{artist}%20track:{song}', type='track')  # search using song and artist
        try:
            uri = result['tracks']['items'][0]['uri']
            url = result['tracks']['items'][0]['external_urls']['spotify']
            uri_code = uri.split(':')[2]
        except (IndexError, KeyError) as error:
            # search using song only
            result = self.sp.search(q=f'track:{song}', type='track')
            try:
                uri = result['tracks']['items'][0]['uri']
                url = result['tracks']['items'][0]['external_urls']['spotify']
                uri_code = uri.split(':')[2]
            except (IndexError, KeyError) as error:
                log.add_log_entry(
                    entry=f'song not found on spotify using song: {song}, artist: {artist}', is_error=True)
                return False
        log.add_log_entry(entry=f'song uri code found, uri code: {uri_code}')
        return uri_code

    def get_top_song_info(self, date):
        """takes a string input as date YYYY-MM-DD and finds information on the billboard top 100 number 1 on that date
        returns a dictionary of strings with keys ''link'-the spotify link to the song, 'artist'-the artist, 'song'-the song,
        'date'-YYYY-MM-DD """
        log.add_log_entry(entry=f'trying to find number one song on {date}')

        song_data = self.scrape_top_song(date)
        if song_data:
            song, artist = song_data['song'], song_data['artist']
            uri_code = self.find_song_uri(song, artist)
            if uri_code:
                link = f'https://open.spotify.com/track/{uri_code}'
                log.add_log_entry(
                    entry=f'song data returned for {song}, {artist}, {link}')
                return {'link': link, 'artist': artist, 'song': song, 'date': date, 'song_found': True}
            else:
                log.add_log_entry(entry='no song data returned', is_error=True)
                return {'date': date, 'song_found': False}
        else:
            log.add_log_entry('no song data returned', is_error=True)
            return {'date': date, 'song_found': False}
