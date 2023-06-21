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
    """
    AWS Lambda function to retrieve a NASA image of the day and tweet it.

    Returns:
    dict: A response object with the status code and the success message or an error message
    """
    try:
        # Retrieve NASA image data from NASA API
        image_data = get_nasa_image()

        title = image_data['title']
        image_obj = image_data['image']

        # Compose the tweet message
        message = write_nasa_message(title)

        logger.info('tweet_image function called')

        # Invoke the 'twiter_bot_tweet_image' lambda function
        response = lambda_client.invoke(
            FunctionName='twiter_bot_tweet_image',
            InvocationType='RequestResponse',
            Payload=json.dumps({'message': message, 'image': image_obj})
        )

        response_payload = json.loads(response['Payload'].read())

        # Handle the response from the 'tweet_image' Lambda function
        if 'FunctionError' in response or response_payload.get('statusCode') != 200:
            logger.error('Error sending tweet')
            logger.error(response_payload)
            raise Exception(response_payload)
        
        if response['StatusCode'] == 200:
            logger.info('Tweet successfully sent')
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Image tweet successfully sent!',
                }),
            }
        else:
            logger.error(response['StatusCode'])
            raise Exception(f'Tweet was not sent. status code {response["StatusCode"]}.')
            
    except Exception as e:
        logger.exception('An error occurred, traceback message:\n {}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred: {}'.format(e)
            }),
        }
        

def get_nasa_image():
    """
    Connects to the NASA image of the day API.

    Returns:
    dict: A dictionary containing the title of the image and the image (as a base64 encoded string)
    """
    logger.info('getting nasa image from nasa api')
    
    try:
        params = {'api_key': environ.get('NASA_API_KEY')}
        response = get('https://api.nasa.gov/planetary/apod?', params=params)
        
        if response.status_code == 200:
            logger.info('NASA API returned response with 200 status code')
            nasa_data = response.json()
            
            title = nasa_data['title']
            # Get the image URL from the NASA API
            image_url = nasa_data['hdurl']
            
            response = get(image_url, stream=True)  # Stream the image
            image_bytes = response.content
            image_base64_str = base64.b64encode(image_bytes).decode('utf-8') # Encode the image to base64
            
            image_data = {'title': title, 'image': image_base64_str}
            
            logger.info('NASA image successfully streamed using URL retrieved from API')
            return image_data
        else:
            logger.error(f'Error getting data from NASA API, status code: {response.status_code}')
            raise Exception(f'Error getting data from NASA API, status code: {response.status_code}, {response.text}')
    except Exception as e:
        logger.error(f'Error getting NASA image: {e}')
        raise Exception(f'Error getting NASA image: {e}')


def write_nasa_message(data):
    """
    Composes a tweet message from the given NASA image data.

    Parameters:
    data (dict): NASA image data

    Returns:
    str: The composed tweet message
    """
    title = data
    message = f"The NASA image of the day today !\n{title}"
    return message
