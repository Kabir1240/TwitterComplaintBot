import time
import os
import json
from selenium import  webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv


load_dotenv()
EXPECTED_SPEEDS_PATH = "expected_speeds.json"
TWITTER_CREDS_PATH = "twitter_creds.json"
TWITTER_URL = "https://twitter.com/"
SPEEDNET_URL = "https://www.speedtest.net/"
SPEEDNET_LOAD_TIME = 100


def get_driver() -> webdriver:
    """
    creates a selenium chrome webdriver with custom options
    Returns: selenium webdriver
    """

    # use this if you want to use your normal browser
    user_data_dir = os.environ.get("USER_DATA_DIR")

    # add chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)

    return driver


class TwitterComplaintBot:
    def __init__(self) -> None:
        """
        if your internet speeds are below the threshold, tags your ISP on Twitter and complains
        """
        with open(EXPECTED_SPEEDS_PATH, 'r') as file:
            expected_speeds = json.load(file)
        
        self.driver = get_driver()
        
        download_speed, upload_speed = self.get_internet_speed()

        if download_speed < expected_speeds["download"] or upload_speed < expected_speeds["upload"]:
            message = (f"Hey Internet Provider, why is my internet speed {download_speed}down/{upload_speed}up when I "
                       f"pay for {expected_speeds['download']}down/{expected_speeds['upload']}up?")
            self.tweet_at_provider(message)
    
    def get_internet_speed(self) -> tuple[float, float]:
        """
        gets your current internet performance speeds from speedtest.net
        Returns: (download_speed, upload_speed)
        """

        print("======= Getting Internet Speeds =======")
        self.driver.get(SPEEDNET_URL)
        start_button = self.driver.find_element(By.CSS_SELECTOR,
                                                '[aria-label="start speed test - connection type multi"]')
        start_button.click()
        
        time.sleep(SPEEDNET_LOAD_TIME)

        download_speed = self.driver.find_element(By.CSS_SELECTOR,
                                                  ".result-data-large.number.result-data-value.download-speed").text
        upload_speed = self.driver.find_element(By.CSS_SELECTOR,
                                                ".result-data-large.number.result-data-value.upload-speed").text

        print(f"download: {download_speed}Mbps, upload: {upload_speed}Mbps")
        return float(download_speed), float(upload_speed)
    
    def tweet_at_provider(self, message) -> None:
        """
        tweets @ your internet provider, the message provided
        Args:
            message: The message to tweet @ your ISP

        Returns: None
        """

        with open(TWITTER_CREDS_PATH, 'r') as file:
            twitter_creds = json.load(file)

        self.driver.get(TWITTER_URL)
        self.login_to_twitter(twitter_creds["username"], twitter_creds["password"])

        # find tweet field
        tweet_field = self.driver.find_element(By.CSS_SELECTOR,
                                               ".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
        tweet_field.send_keys(message)

        # press post
        post_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid = "tweetButtonInline"]')
        post_button.click()

        print("posted tweet")

    def login_to_twitter(self, username: str, password: str) -> None:
        """
        logs you into twitter from an incognito tab
        Args:
            username: Twitter username handle or email
            password: Twitter password

        Returns: None
        """
        # close welcome message
        cancel_button = self.driver.find_element(By.CSS_SELECTOR, "button.css-175oi2r.r-sdzlij.r-1phboty.r-rs99b7.r"
                                                                  "-lrvibr.r-2yi16.r-1qi8awa.r-3pj75a.r-1loqt21.r"
                                                                  "-o7ynqc.r-6416eg.r-1ny4l3l")
        cancel_button.click()

        # find and click the signin button
        sign_in_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid = "loginButton"]')
        sign_in_button.click()

        time.sleep(10)

        # enter username
        username_entry = self.driver.find_element(By.CSS_SELECTOR, '[autocomplete = "username"]')
        username_entry.send_keys(username, Keys.ENTER)

        # enter password and login
        password_entry = self.driver.find_element(By.CSS_SELECTOR, '[autocomplete = "current-password"]')
        password_entry.send_keys(password)
