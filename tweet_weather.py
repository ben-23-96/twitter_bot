import logging
import boto3
import json
from requests import get
from datetime import datetime, timedelta
from os import environ

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize boto3 client for lambda
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    AWS Lambda function to retrieve weather data and invoke a tweet function.

    Returns:
    dict: A response object with the status code and the success message or an error message
    """

    try:
        # Retrieve weather data and write tweet message
        weather_data = get_weather()
        message = write_weather_message(weather_data)
        
        # Invoke the 'tweet_text' Lambda function
        response = lambda_client.invoke(
            FunctionName='twiter_bot_tweet_text',
            InvocationType='RequestResponse',
            Payload=json.dumps({'message': message})
        )
        logger.info('tweet_text function called')

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
                'weather_data': weather_data,
            }),
        }
        else:
            logger.error(response['StatusCode'])
            raise Exception(
                f'Tweet was not sent. status code {response["StatusCode"]}. response {response.text}'
            )

    except Exception as e:
        # log error and return unsuccessful response
        logger.exception(
            'An error occurred, traceback message:\n {}'.format(e)
        )

        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }


def get_weather():
    """
    Fetches weather data from the OpenWeatherMap API

    Returns:
    dict: Weather data for the next seven days
    """

    logger.info('getting weather data from weather api')

    # Set API parameters
    params = {
        'lat': 53.57,
        'lon': -2.42,
        'exclude': 'current,minutely,hourly,alerts',
        'units': 'metric',
        'appid': environ.get('WEATHER_API_KEY')
    }

    try:
        # Send request to API
        response = get(
            'https://api.openweathermap.org/data/2.5/onecall?', params=params
        )
        weather_data = response.json()['daily']
    except KeyError:
        logger.error(
            f'error getting weather data status code of request: {response.status_code}'
        )
        logger.error(response.json())
        raise KeyError('no weather data returned from api')
    except Exception:
        logger.error('error retrieving data from api')
        raise Exception

    logger.info('weather data returned from api')
    return weather_data


def write_weather_message(data):
    """
    Constructs a tweet message from weather data

    Parameters:
    data (dict): Weather data for the next seven days

    Returns:
    str: A message string containing the weather data
    """

    message = 'The next 7 days weather:\n'
    day = datetime.now()
    
    for weather in data:
        # Extract weather data
        day_name = day.strftime('%A')
        type = weather['weather'][0]['main']
        temp = weather['temp']['day']

        # Append data to message
        message = message + f"{day_name} {type} {temp}C\n"
        day = day + timedelta(days=1)

    return message
