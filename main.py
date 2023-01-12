import tweepy
import re
import yfinance as yf
import pandas as pd
from datetime import datetime, time
import configparser
from textblob import TextBlob
from matplotlib import pyplot as plt
from workalendar.usa import NewYork
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
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

stocks = input('Enter 5 or more ticker symbols, separated by commas: ').upper()
stocks = stocks.split(", ")
stocks = ['$' + x for x in stocks]

start_date = datetime.now().date()

# Create a list of market holidays, where the stock exchange is closed
cal = NewYork()
cal.holidays(2023)

# Create a dataframe of stock market holidays
holiday_df = pd.DataFrame(cal.holidays(2023), columns=['Date', 'Holiday'])
holiday_df = holiday_df.drop([0, 3, 4, 9, 10, 11, 12])  # Remove non-market-holidays

# Add additional market holidays
holiday_df.loc[9] = ['2023-04-07', 'Good Friday']
holiday_df.loc[10] = ['2023-06-19', 'Juneteenth']

holiday_df['Date'] = pd.to_datetime(holiday_df['Date'])
tickers = []  # empty list to store the ticker of appended tweets
all_tweets = []  # empty list to store all tweets being used


def retrieve_tweets():
    global df_x

    def search_ticker():
        global stock_search_date
        tweets_per_day = 0
        current_day = None
        for tweet in cursor.items(limit=10000):
            day = tweet.created_at
            tweet_date = pd.to_datetime(day.date().strftime('%Y-%m-%d'))
            # Only add tweets which were made before market open on weekdays
            if day.time() < time(hour=9, minute=30) and day.weekday() < 5:
                # Do not add tweets which were made on stock market holidays
                if not holiday_df['Date'].eq(tweet_date).any():
                    if current_day is None:
                        current_day = day.date()
                        stock_search_date = current_day
                    # Only append tweets from the same trading day
                    if day.date() != current_day:
                        break
                    if tweets_per_day < 100:
                        all_tweets.append(tweet.text)
                        tickers.append(search_parameters['q'])
                        tweets_per_day += 1
                    else:
                        break
        return

    for stock in stocks:
        search_parameters = {
            'q': stock,
            'lang': 'en',
            'count': 100,
            'until': start_date,
            'tweet_mode': 'ext'
        }
        cursor = tweepy.Cursor(api.search_tweets, **search_parameters)
        search_ticker()

    df = pd.DataFrame(all_tweets, columns=['Tweets'])
    df['Ticker'] = tickers

    # Clean up tweet texts for sentiment analysis
    def clean_tweets(text):
        text = re.sub(r'@[A-Za-z0-9]+', '', text)  # Removes @ mentions
        text = re.sub(r'#', '', text)  # Removes hashtags
        text = re.sub(r'RT\s+', '', text)  # Removes retweets
        text = re.sub(r'http\S+', '', text)  # Removes hyperlinks
        text = re.sub(r'www.\S+', '', text)  # Removes hyperlinks
        return text

    # Apply the tweet-cleaning function to df
    df['Tweets'] = df['Tweets'].apply(clean_tweets)

    # Get subjectivity (how opinionated/subjective a text is)
    def get_subjectivity(text):
        return TextBlob(text).sentiment.subjectivity

    # Get polarity (how positive/negative text is)
    def get_polarity(text):
        return TextBlob(text).sentiment.polarity

    # Create Subjectivity and Polarity df columns
    df['Subjectivity'] = df['Tweets'].apply(get_subjectivity)
    df['Polarity'] = df['Tweets'].apply(get_polarity)

    # Create a second df for regression analysis
    df_x = df[['Subjectivity', 'Polarity', 'Ticker']].copy()

    # Get the average subjectivity and polarity of each ticker's tweets
    df_x = df_x.groupby(df_x['Ticker']).mean()

    return df_x


def stock_trend(stocks):
    global df_y

    stocks = [s[1:] for s in stocks]  # Remove cashtag from ticker symbols

    df_y = pd.DataFrame()

    for stock in stocks:
        # Get the Ticker object for the stock
        ticker = yf.Ticker(stock)

        # Get the stock info
        info = ticker.info

        # Get the open and close prices
        open_price = info['regularMarketOpen']
        close_price = info['regularMarketPreviousClose']

        # Calculate the percent change between the open and close prices
        pct_change = ((close_price - open_price) / open_price) * 100

        # Add the percent change to the DataFrame
        df_y[stock] = [pct_change]

    return df_y


def linear_regression():
    retrieve_tweets()
    stock_trend(stocks)

    # Twitter sentiment (polarity) of ticker symbol is the independent variable
    X = df_x['Polarity'].to_numpy()
    X = X.reshape(-1, 1)

    # Percentage change of the stock is the dependent variable
    y = df_y.loc[[0]].to_numpy()
    y = y.reshape(-1, 1)

    regressor = LinearRegression()
    regressor.fit(X, y)

    y_pred = regressor.predict(X)
    r2 = r2_score(y, y_pred)

    # Plot the data points
    plt.scatter(X, y, color='g')

    # Plot the regression line
    plt.plot(X, regressor.predict(X), marker='o', color='blue')

    plt.xlabel('Polarity')
    plt.ylabel('Percentage Change')
    plt.title('Twitter Sentiment vs Stock Price')
    text = f"R-Squared = {r2:.3f}"
    plt.text(.8, 1, text, transform=plt.gca().transAxes)

    return plt.show()


linear_regression()
