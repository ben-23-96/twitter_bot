import logging
from requests import get
from random import choice
from os import environ
import json
import boto3

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initiate boto3 client for lambda
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    try:
        news_data = get_news()
        message = write_news_message(news_data)
        
        # Invoke the 'tweet_text' Lambda function
        response = lambda_client.invoke(
            FunctionName='twiter_bot_tweet_text',
            InvocationType='RequestResponse',
            Payload=json.dumps({'message': message})
        )
        
        if 'FunctionError' in response:
            error_response = json.loads(response['Payload'].read())
            logger.error('Error sending tweet')
            logger.error(error_response)
            raise Exception(error_response)
        
        # Handle the response from the 'tweet_text' Lambda function
        if response['StatusCode'] == 200:
            logger.info('Tweet successfully sent')
        else:
            logger.error(response['StatusCode'])
            logger.error()
            raise Exception(f'Tweet was not sent. status code {response["StatusCode"]}.')

        return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Tweet successfully sent!',
                    'news_data': news_data,
                }),
            }
    except Exception as e:
        logger.error('An error occurred: {}'.format(e))
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }


def get_news():
    """connects to the newsapi using a random news category, returns a dictionary containing the data of the top article and the news category of it"""
    logger.info('getting news data from news api')

    categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology']
    category = choice(categories)
    params = {'apikey': environ.get('NEWS_API_KEY'), 
              'category': category, 
              'language': 'en'}
    response = get('https://newsapi.org/v2/top-headlines?', params=params)

    try:
        article_data = response.json()['articles'][0]
        news_data = {'article_data': article_data, 'news_category': category}
    except KeyError:
        logger.error(f'error getting news data status code of request: {response.status_code}')
        logger.error(response.json())
        raise KeyError('No article data returned from api.')

    logger.info('news data returned from api')
    return news_data

def write_news_message(data):
    """input is dictionary from the get_news function, writes a message to be tweeted'"""
    logger.info('writing message to be tweeted')

    news_article = data['article_data']
    news_topic = data['news_category']

    article_string = f"\n{news_article['title']}\n{news_article['url']}"
    message_options = [f"some fascinating {news_topic} news:{article_string}",
                       f"wow look at this {news_topic} news:{article_string}",
                       f"interesting developments in the {news_topic} world, read about it here: {article_string}",
                       f"never a dull moment in {news_topic}. {article_string}",
                       f"{news_topic} news that has peaked my interest: {article_string}",
                       f"can't believe this {news_topic} news. {article_string}",
                       f"seen this {news_topic} news coming a mile off. {article_string}",
                       f"been waiting a long time for {news_topic} news like this. {article_string}",
                       f"{news_topic}! {news_topic}! read all about it!! {article_string}"]
    
    message = choice(message_options)
    return message

print(lambda_handler(event="", context=""))