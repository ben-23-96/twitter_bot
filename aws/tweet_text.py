import logging
from os import environ
from requests_oauthlib import OAuth1Session
import json

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        message = event['message']
        logger.info('tweet_text function called')

        TWEET_URL = 'https://api.twitter.com/2/tweets'

        oauth = OAuth1Session(
            environ.get("TWITTER_API_KEY"),
            client_secret=environ.get("TWITTER_API_SECRET"),
            resource_owner_key=environ.get("TWITTER_API_ACCESS_TOKEN"),
            resource_owner_secret=environ.get(
                "TWITTER_API_ACCESS_TOKEN_SECRET"),
        )

        tweet = {"text": message}
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
