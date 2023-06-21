import logging
from requests import get
from random import choice
from os import environ
import json
import boto3

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize boto3 client for lambda
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    AWS Lambda function to retrieve news data and invoke a tweet function.

    Returns:
    dict: A response object with the status code and the success message or an error message
    """

    try:
        # Retrieve news data and write tweet message
        news_data = get_news()
        message = write_news_message(news_data)

        # Invoke the 'tweet_text' Lambda function
        response = lambda_client.invoke(
            FunctionName='twiter_bot_tweet_text',
            InvocationType='RequestResponse',
            Payload=json.dumps({'message': message})
        )

        # Load the response payload
        response_payload = json.loads(response['Payload'].read())

        # Check if there was an error invoking the function
        if 'FunctionError' in response or response_payload.get('statusCode') != 200:
            logger.error('Error sending tweet')
            logger.error(response_payload)
            raise Exception(response_payload)

        # Check the response status code if tweet successful return succesful response else raise exception
        if response['StatusCode'] == 200:
            logger.info('Tweet successfully sent')
            return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Tweet successfully sent!',
                'news_data': news_data,
            }),
        }
        else:
            logger.error(response['StatusCode'])
            raise Exception(
                f'Tweet was not sent. status code {response["StatusCode"]}. reponse {response.text}'
            )

    except Exception as e:
        # log error and return unsuccessful response
        logger.exception(
            'An error occurred, traceback message:\n {}'.format(e))

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }


def get_news():
    """
    Fetches news data from the News API with a random category

    Returns:
    dict: Top news article data for a random category
    """

    logger.info('getting news data from news api')

    # Set up possible news categories and choose one randomly
    categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
    category = choice(categories)

    # Set API parameters
    params = {
        'apikey': environ.get('NEWS_API_KEY'),
        'category': category,
        'language': 'en'
    }

    # Send request to API
    response = get('https://newsapi.org/v2/top-headlines?', params=params)

    try:
        # Extract top article data and category
        article_data = response.json()['articles'][0]
        news_data = {'article_data': article_data, 'news_category': category}
    except KeyError:
        logger.error(
            f'error getting news data status code of request: {response.status_code}'
        )
        logger.error(response.json())
        raise KeyError('No article data returned from api.')

    logger.info('news data returned from api')
    return news_data


def write_news_message(data):
    """
    Constructs a tweet message from news data

    Parameters:
    data (dict): A dictionary containing news data

    Returns:
    str: A message string for the tweet
    """

    logger.info('writing message to be tweeted')

    # Extract news article data and category
    news_article = data['article_data']
    news_topic = data['news_category']

    # Construct message for tweet
    article_string = f"\n{news_article['title']}\n{news_article['url']}"
    message_options = [
        f"some fascinating {news_topic} news:{article_string}",
        f"wow look at this {news_topic} news:{article_string}",
        f"interesting developments in the {news_topic} world, read about it here: {article_string}",
        f"never a dull moment in {news_topic}. {article_string}",
        f"{news_topic} news that has peaked my interest: {article_string}",
        f"can't believe this {news_topic} news. {article_string}",
        f"seen this {news_topic} news coming a mile off. {article_string}",
        f"been waiting a long time for {news_topic} news like this. {article_string}",
        f"{news_topic}! {news_topic}! read all about it!! {article_string}",
        f"Intriguing update in the {news_topic} scene:{article_string}",
        f"Shaking up the {news_topic} world with this: {article_string}",
        f"Keep an eye on this unfolding {news_topic} story: {article_string}",
        f"A must-read {news_topic} update: {article_string}",
        f"Hot off the press, {news_topic} news. {article_string}",
        f"In case you missed this {news_topic} news. {article_string}"
    ]

    # Choose one message option randomly
    message = choice(message_options)
    return message
