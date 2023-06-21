import logging
from os import environ
from requests_oauthlib import OAuth1Session
import json

# Setting up logging to catch and record errors
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda function to send a tweet from a bot account.

    Parameters:
    event (dict): AWS Lambda uses this parameter to pass in event data to the handler. 
                  It should include message (str). The message to be tweeted.

    Returns:
    dict: A response object with the status code and the tweet message or an error message
    """

    try:
        # Extracting the message from the event object
        message = event['message']
        logger.info('tweet_text function called')

        # Twitter API url for creating a new tweet
        TWEET_URL = 'https://api.twitter.com/2/tweets'

        # Setting up OAuth session using environment variables
        oauth = OAuth1Session(
            environ.get("TWITTER_API_KEY"),
            client_secret=environ.get("TWITTER_API_SECRET"),
            resource_owner_key=environ.get("TWITTER_API_ACCESS_TOKEN"),
            resource_owner_secret=environ.get(
                "TWITTER_API_ACCESS_TOKEN_SECRET"),
        )

        # Constructing the tweet object
        tweet = {"text": message}
        
        # Sending a POST request to the Twitter API
        tweet_res = oauth.post(url=TWEET_URL, json=tweet)

        # Checking if the tweet was successful based on the status code
        if tweet_res.status_code == 201:
            logger.info(f'tweet successful, message: {message}')
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Tweet successfully sent! message: {message}',
                }),
            }
        else:
            # Log error and raise an exception if the tweet wasn't successful
            logger.error(
                f'error sending tweet, message: {message}, reponse code of post request: {tweet_res.status_code}')
            logger.error(tweet_res.json())
            
            raise Exception({
                'message': 'error sending tweet',
                'response_code': tweet_res.status_code,
                'response_json': tweet_res.json(),
            })

    except Exception as e:
        # Logging the exception information
        logger.exception(
            'An error occurred, traceback message:\n {}'.format(e))

        # Returning the error response
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }

