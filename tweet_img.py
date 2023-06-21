from requests_oauthlib import OAuth1Session
from os import environ
import logging
import json
import base64

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants for API URLs
TWEET_URL = 'https://api.twitter.com/2/tweets'
MEDIA_UPLOAD_URL = 'https://upload.twitter.com/1.1/media/upload.json'

def lambda_handler(event, context):
    """
    AWS Lambda function to post a tweet with an image.

    Parameters:
    event (dict): AWS Lambda uses this parameter to pass in event data to the handler. 
                  It should include 'image' (base64 encoded string) and 'message' (the text string that will be tweeted)

    Returns:
    dict: A response object with the status code and the success message or an error message
    """
    try:
        # Extract image and message from event
        image_base64_str = event['image']
        message = event['message']

        # Decode the base64 string into bytes
        image_bytes = base64.b64decode(image_base64_str)

        # Create an OAuth1Session
        oauth = OAuth1Session(
            environ.get("TWITTER_API_KEY"),
            client_secret=environ.get("TWITTER_API_SECRET"),
            resource_owner_key=environ.get("TWITTER_API_ACCESS_TOKEN"),
            resource_owner_secret=environ.get("TWITTER_API_ACCESS_TOKEN_SECRET"),
        )

        # Prepare the files dict for the POST request
        files = {'media': image_bytes}

        # Upload the image so it can be attached to a tweet
        upload_res = oauth.post(MEDIA_UPLOAD_URL, files=files)

        # Extract the 'media_id_string' from the response
        upload_res_data = upload_res.json()
        media_id = upload_res_data['media_id_string']

        # Prepare the tweet data
        tweet = {"text": message, "media": {"media_ids": [media_id]}}

        # Post the tweet
        tweet_res = oauth.post(url=TWEET_URL, json=tweet)

        # Handle the response
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
