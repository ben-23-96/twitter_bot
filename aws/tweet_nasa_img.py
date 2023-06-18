import logging
from os import environ
from requests import get
import boto3
import json
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initiate boto3 client for lambda
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    try:
        image_data = get_nasa_image()  # retrieve nasa image from nasa api
        title = image_data['title']
        image_obj = image_data['image']
        message = write_nasa_message(title)
        logger.info('tweet_image function called')

        response = lambda_client.invoke(
            FunctionName='twiter_bot_tweet_image',
            InvocationType='RequestResponse',
            Payload=json.dumps({'message': message, 'image': image_obj})
        )

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
            logger.error()
            raise Exception(
                f'Tweet was not sent. status code {response["StatusCode"]}.')
        return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Image tweet successfully sent!',
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
        


def get_nasa_image():
    """connects to the nasa image of the day API, returns dictionary containing the title of the image and the image"""
    logger.info('getting nasa image from nasa api')
    try:
        params = {'api_key': environ.get('NASA_API_KEY')}
        response = get('https://api.nasa.gov/planetary/apod?', params=params)
        if response.status_code == 200:
            logger.info('nasa api returned response with 200 status code')
            nasa_data = response.json()
        
            title = nasa_data['title']
            # get the image url from the nasa api
            image_url = nasa_data['hdurl']
        
            response = get(image_url, stream=True)  # stream the image
            image_bytes = response.content
            image_base64_str = base64.b64encode(image_bytes).decode('utf-8')
            image_data = {'title': title, 'image': image_base64_str}
        
            logger.info(
                'nasa image successfully streamed using url retrieved from api')
            return image_data
        else:
            logger.error(
                f'error getting data from nasa api code of request: {response.status_code}')
            logger.error(response.text)
            raise Exception(f'error getting data from nasa api code of request: {response.status_code}, {response.text}')
    except Exception as e:
        logger.error(f'error getting nasa image: {e}')
        raise Exception(f'error getting nasa image: {e}')


def write_nasa_message(data):
    """input is a dictionary from the Topic class's get_nasa_image method, writes a message to be tweeted"""

    title = data
    message = f"cool image from nasa\n{title}"
    return message

