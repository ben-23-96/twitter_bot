from datetime import datetime, date
import logging
import boto3
import json

# set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        birthdays_today = check_birthdays()
        for birthday in birthdays_today:
            bday_tweet = write_birthday_message(birthday)
            logger.info(f'tweet_text function called for {birthday}')
            tweet_text(bday_tweet)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Birthday messages sent successfully!',
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

def check_birthdays():
    """reads the birthdays table and checks the data to see if any of the birthdays match the current date,
    if there are birthdays today returns a list of dictionaires, each dictionary containing the twitter username, 'user',
    and their age, 'age'.
    if there are no birthdays returns a empty list"""
    logger.info('checking datbase for birthdays')
   
    dynamodb = boto3.resource('dynamodb') # Instantiate a DynamoDB client
    table = dynamodb.Table('Birthdays')
    # Get today's date as a string
    today = datetime.now()

    # Scan the entire table
    response = table.scan()
    todays_birthdays = []
    for item in response['Items']:
        bday = datetime.strptime(item['birthday'], '%Y-%m-%d')
        if bday.day == today.day and bday.month == today.month:  # check if birthday is today
            logger.info(f"birthday found on {today} for {item['username']}")
            age = round((today - bday).days/365)
            todays_birthdays.append({'user': f"@{item['username']}", 'age': age})
    print(todays_birthdays)
    return todays_birthdays
    

def write_birthday_message(data):
    """input is list item containing a dictionary from the Birthday class's check_birthdays method, writes a message to be tweeted"""
    user = data['user']
    age = data['age']
    message = f"{user} Happy Birthday, you are {age} today, well done."
    print(message)
    return message
    

def tweet_text(message):
    
    lambda_client = boto3.client('lambda') # Initiate boto3 client for lambda
    # Invoke the 'tweet_text' Lambda function
    response = lambda_client.invoke(
        FunctionName='twiter_bot_tweet_text',
        InvocationType='RequestResponse',
        Payload=json.dumps({'message': message})
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

