from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from requests import get
from bs4 import BeautifulSoup
from os import environ
import logging
import json

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    date = event['date']
    try:
        song_finder = SpotifySongFinder()
        song_info = song_finder.get_top_song_info(date)
        reply = write_spotify_message(song_info)
        logger.info('spotify reply created successfully')
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Song found successfully',
                'reply': reply
            }),
        }
    except Exception as e:
        logger.exception(
            'An error occurred, traceback message:\n {}'.format(e))

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }


class SpotifySongFinder:
    def __init__(self):
        """class that finds the top song on a given date through web scraping and finds that song in spotify
        using the spotify API"""

        self.cid = environ.get('SPOTIFY_CID')
        self.secret = environ.get('SPOTIFY_SECRET')
        self.auth_manager = SpotifyClientCredentials(
            client_id=self.cid, client_secret=self.secret)
        self.sp = Spotify(client_credentials_manager=self.auth_manager)
        self.songs = ''

    def scrape_top_song(self, date):
        """takes a string input of date YYYY-MM-DD and finds the billboard top 100 number 1
        on that date, returning the song name and artist as strings"""

        logger.info(f'scraping billboard for top song on date: {date}')
        try:
            response = get(
                f'https://www.billboard.com/charts/hot-100/{date}/')  # get website html

            website_html = response.text

            soup = BeautifulSoup(website_html, 'html.parser')

            soup_data = soup.find_all(
                name='li', class_='o-chart-results-list__item', limit=4)  # scrap page for top song

            soup_song = soup_data[3]

            song = soup_song.find(name='h3', class_='c-title',
                                  id="title-of-a-story").string.strip('\n')
            artist = soup_song.find(
                name='span', class_='c-label').string.strip('\n')
            logger.info(
                f'song found on billboard song: {song}, artist: {artist}')
            return {'song': song, 'artist': artist}
        except Exception as e:
            logger.error(
                f'error scraping the song from billboard for date: {date}, error: {e}')
            raise Exception(
                f'error scraping the song from billboard for date: {date}, error: {e}')

    def find_song_uri(self, song, artist):
        """takes a string inputs for a song and artist and returns the spotify uri code
        for that song as a string"""

        logger.info('finding song uri code on spotify')
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
                logger.error(
                    f'song not found on spotify using song: {song}, artist: {artist}')
                raise Exception(
                    f'song not found on spotify using song: {song}, artist: {artist}, error {error}')
        logger.info(f'song uri code found, uri code: {uri_code}')
        return uri_code

    def get_top_song_info(self, date):
        """takes a string input as date YYYY-MM-DD and finds information on the billboard top 100 number 1 on that date
        returns a dictionary of strings with keys ''link'-the spotify link to the song, 'artist'-the artist, 'song'-the song,
        'date'-YYYY-MM-DD """
        logger.info(f'trying to find number one song on {date}')
        try:
            song_data = self.scrape_top_song(date)

            song, artist = song_data['song'], song_data['artist']
            uri_code = self.find_song_uri(song, artist)

            link = f'https://open.spotify.com/track/{uri_code}'
            logger.info(f'song data returned for {song}, {artist}, {link}')
            return {'link': link, 'artist': artist, 'song': song, 'date': date}
        except Exception as e:
            logger.error(f'error getting top song info')
            raise Exception(f'error getting top song info error: {e}')


def write_spotify_message(data):
    """input is a dictionary from the Spotify class's get_top_song_info method, writes a message to be tweeted"""

    link = data['link']
    song = data['song']
    artist = data['artist']
    date = data['date']
    message = f'The number one song on {date} was {song} by {artist}, listen here:\n{link}'
    return message
