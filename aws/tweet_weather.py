import logging
import boto3
import json
from requests import get
from datetime import datetime, timedelta
from os import environ

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initiate boto3 client for lambda
lambda_client = boto3.client('lambda')


def lambda_handler(event, context):

    try:
        weather_data = get_weather()
        message = write_weather_message(weather_data)
        # Invoke the 'tweet_text' Lambda function
        response = lambda_client.invoke(
            FunctionName='twiter_bot_tweet_text',
            InvocationType='RequestResponse',
            Payload=json.dumps({'message': message})
        )
        logger.info('tweet_text function called')
        response_payload = json.loads(response['Payload'].read())
        if 'FunctionError' in response or response_payload.get('statusCode') != 200:
            logger.error('Error sending tweet')
            logger.error(response_payload)
            raise Exception(response_payload)
        # Handle the response from the 'tweet_text' Lambda function
        if response['StatusCode'] == 200:
            logger.info('Tweet successfully sent')
        else:
            logger.error(response['StatusCode'])
            raise Exception(
                f'Tweet was not sent. status code {response["StatusCode"]}.')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Tweet successfully sent!',
                'weather_data': weather_data,
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


def get_weather():
    """connects to the openweather api, returns a dictionary containing information on the next 7 days weather"""
    logger.info('getting weather data from weather api')

    params = {'lat': 53.57,
              'lon': -2.42,
              'exclude': 'current,minutely,hourly,alerts',
              'units': 'metric',
              'appid': environ.get('WEATHER_API_KEY')}

    try:
        response = get(
            'https://api.openweathermap.org/data/2.5/onecall?', params=params)
        weather_data = response.json()['daily']
    except KeyError:
        logger.error(
            f'error getting weather data status code of request: {response.status_code}')
        logger.error(response.json())
        raise KeyError('no weather data returned from api')
    except Exception:
        logger.error('error retrieving data from api')
        raise Exception

    logger.info('weather data returned from api')
    return weather_data


def write_weather_message(data):
    """input is a dictionary from the get_weather function, writes a message to be tweeted"""

    message = 'The next 7 days weather:\n'
    day = datetime.now()
    for weather in data:
        day_name = day.strftime('%A')
        type = weather['weather'][0]['main']
        temp = weather['temp']['day']
        id = weather['weather'][0]['id']
        message = message + f"{day_name} {type} {temp}C\n"
        day = day + timedelta(days=1)

    return message
