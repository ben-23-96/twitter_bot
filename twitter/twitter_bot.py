from datetime import datetime, timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from spotify.spotify_song import SpotifySongFinder
from messages.message_writer import Message
from birthday.birthday_wisher import Birthday
from dotenv import load_dotenv
from os import getenv


class Twitter_bot:
    def __init__(self):
        """class that uses selenium to operate a bot that can post and reply on twitter"""

        self.service = Service(executable_path=ChromeDriverManager().install())
        #self.option = webdriver.ChromeOptions()
        # self.option.add_argument(
        #    '--disable-blink-features=AutomationControlled')
        # self.option.add_argument("window-size=1280,800")
        #self.option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
        self.driver = webdriver.Chrome(service=self.service)
        self.email = getenv('EMAIL')
        self.password = getenv('PASSWORD')
        self.username = getenv('TWITTER_USERNAME')

    def login_twitter(self):
        """uses selenium to open twitter in the browser and logs into to the bots twitter account"""

        self.driver.get("http://twitter.com")

        self.driver.maximize_window()

        self.driver.delete_all_cookies()

        sign_in = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/login"]')))  # '//*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[5]/a/div')))
        self.driver.execute_script("arguments[0].click();", sign_in)

        email_input = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
            (By.NAME, 'text')))
        email_input.send_keys(self.email + Keys.ENTER)
        try:
            password_input = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
                (By.NAME, 'password')))
            password_input.send_keys(self.password + Keys.ENTER)
        except:
            username_input = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
                (By.NAME, 'text')))
            username_input.send_keys(self.username + Keys.ENTER)
            password_input = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
                (By.NAME, 'password')))
            password_input.send_keys(self.password + Keys.ENTER)
        sleep(20)

    def tweet_text(self, message):
        """takes a messsage as string input and tweets the message and quits the browser.
        Bot must already be logged in."""
        try:
            tweet_box = WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'DraftEditor-root')))
            tweet_box.click()

            tweet_input = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'public-DraftEditorPlaceholder-root')))
            ActionChains(self.driver).move_to_element(
                tweet_input).send_keys(f"{message}").perform()

            tweet_button = self.driver.find_element(
                By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[2]/div[3]/div/span/span')
            self.driver.execute_script("arguments[0].click();", tweet_button)
            sleep(10)
            self.driver.quit()
        except:
            self.driver.quit()

    def tweet_image(self, image, message=""):
        """takes the absolute path to an image as a string, and a message as a string,
        proceeds to tweet the image and message and quit the browser.
        Bot must already be logged into twitter."""
        try:
            input_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div/div[1]/input'
            image_path = image
            input_element = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, input_xpath)))
            input_element.send_keys(image_path)
            self.tweet_text(message)
            self.driver.quit()
        except:
            self.driver.quit()

    def find_messages_needing_reply(self):
        """Uses selenium to find which messages need replying to by retrieving the time they were posted
        and seeing if is within the time the bot last ran. Gets the text of the messages that need to be replied to
        as well as the user that sent them and uses them as inputs for the select_reply method. When the replies messages
        have been returned from this method, they are zipped with the selenium object that is the reply button for that message.
        Returns a zip object containing messages to be sent in reply and the seleniuim object for the reply button for each message."""

        sleep(30)
        times = self.driver.find_elements(By.XPATH, '//time')

        current_time = datetime.now()
        messages_needing_reply = []

        for t in times:
            message_time = t.get_attribute('datetime')
            date, time = message_time.split('T')
            year, month, day = date.split('-')
            hour, minutes, seconds = time[:8].split(':')

            tweet_time = datetime(int(year), int(month), int(
                day), int(hour), int(minutes), int(seconds))
            difference = current_time - tweet_time

            if difference <= timedelta(minutes=20):
                messages_needing_reply.append(difference)

        num_messages_needing_reply = len(messages_needing_reply)

        tweets = self.driver.find_elements(
            By.XPATH, '//article//div[@dir="auto"]')

        user_who_tweeted = self.driver.find_elements(
            By.XPATH, '//a[@role="link"]//div[@dir="ltr"]//span')

        reply_messages = []
        count = 0

        for i in range(3, 4*num_messages_needing_reply, 4):
            recieved_tweet = tweets[i].text
            user = user_who_tweeted[count].text
            reply = self.select_reply(recieved_tweet, user)
            reply_messages.append(reply)

        reply_buttons = self.driver.find_elements(
            By.XPATH, '//article//div[@data-testid="reply"]')

        replies_and_reply_buttons = zip(reply_messages, reply_buttons)

        return replies_and_reply_buttons

    def select_reply(self, recieved_tweet, user):
        """Takes a string input of recieved tweet message and another string input of the user who sen tthe message.
        Checks to see what should be done with the message, find spotify song or add to birthday list.
        Returns a message to be sent in reply."""

        tweet_words = recieved_tweet.split()
        if tweet_words[1] == 'spotify':
            song_finder = SpotifySongFinder()
            date = tweet_words[2]
            song_info = song_finder.get_top_song_info(date)
            message = Message()
            reply = message.compose_tweet('spotify', song_info)
            return reply
        elif tweet_words[1] == 'birthday':
            birthday = Birthday()
            date = tweet_words[2]
            print(user, date)
            birthday.add_birthday(user, date)
            return 'your birthdays in the diary'
        else:
            return 'howdy'

    def reply(self):
        """find the messages that need to be replied to by navigating to the mentions page, and then
        calling the find_messages_needing_reply method with returns reply messages and the buttons to click
        for the mentions that will not have been replied to sice the bot last ran this method.
        Loops through replying to each mention without a reply.
        Quits the driver when finished."""

        try:
            notifications = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//a[@href="/notifications"]')))
            notifications.click()
            sleep(6)
            mentions = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//a[@href="/notifications/mentions"]')))
            mentions.click()

            reply_button = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//article//div[@data-testid="reply"]')))

            replies_and_reply_buttons = self.find_messages_needing_reply()

            for reply, button in replies_and_reply_buttons:
                WebDriverWait(self.driver, 60).until(EC.presence_of_element_located(
                    (By.XPATH, '//article//div[@data-testid="reply"]')))
                self.driver.execute_script("arguments[0].click();", button)
                tweet_box = WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'DraftEditor-root')))
                tweet_box.click()
                tweet_input = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'public-DraftEditorPlaceholder-root')))
                ActionChains(self.driver).move_to_element(
                    tweet_input).send_keys(reply).perform()
                tweet_send = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(
                    (By.XPATH, '//div[@data-testid="tweetButton"]'))).click()
                sleep(20)
            self.driver.quit()
        except:
            self.driver.quit()
