from requests_oauthlib import OAuth1Session
from os import environ
import logging
import json
import base64

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TWEET_URL = 'https://api.twitter.com/2/tweets'
MEDIA_UPLOAD_URL = 'https://upload.twitter.com/1.1/media/upload.json'


def lambda_handler(event, context):
    try:
        image_base64_str = event['image']
        message = event['message']
        image_bytes = base64.b64decode(image_base64_str)
        oauth = OAuth1Session(
            environ.get("TWITTER_API_KEY"),
            client_secret=environ.get("TWITTER_API_SECRET"),
            resource_owner_key=environ.get("TWITTER_API_ACCESS_TOKEN"),
            resource_owner_secret=environ.get(
                "TWITTER_API_ACCESS_TOKEN_SECRET"),
        )
    
        files = {'media': image_bytes}
        # upload image using twitter api
        upload_res = oauth.post(MEDIA_UPLOAD_URL, files=files)

        upload_res_data = upload_res.json()
        # media id string indentifing uploaded image
        media_id = upload_res_data['media_id_string']
    
        tweet = {"text": message,
                 "media": {"media_ids": [media_id]}}
        # send a tweet containing the uploaded image indentified by media id string
        tweet_res = oauth.post(url=TWEET_URL, json=tweet)

        if tweet_res.status_code == 201:
            logger.info(f'tweet successful, message: {message}')
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Tweet successfully sent! message: {message}',
                }),
            }
        else:
            logger.error(
                f'error sending tweet, message: {message}, reponse code of post request: {tweet_res.status_code}')
            logger.error(tweet_res.json())
            raise Exception({
                'message': 'error sending tweet',
                'response_code': tweet_res.status_code,
                'response_json': tweet_res.json(),
            })
    
    except Exception as e:
        logger.exception(
            'An error occurred, traceback message:\n {}'.format(e))

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }
    