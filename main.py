import tweepy
import re
import pytz
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, time
import configparser
from textblob import TextBlob
from matplotlib import pyplot as plt
from workalendar.usa import NewYork
plt.style.use('fivethirtyeight')

# Read Configs
config = configparser.ConfigParser()
config.read('config.ini')

# Twitter API Credentials
api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

# Authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

# Make an API object
api = tweepy.API(auth)
