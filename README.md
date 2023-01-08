<h1 align="center">Stock Portfolio Forecasting using Twitter Sentiment Analysis</h1>

<h2 align='center'>Project Description</h2>

The objective of this project is to determine the efficacy of utilizing Twitter users' average sentiment of a stock before market-open to predict the stock's daily-trend. 

To determine the effectiveness of Twitter sentiment analysis for stock trend prediction, the user may enter the ticker symbols of up to 5 stocks in their portfolio. The program will then compare the average sentiment of each ticker symbol, and the daily percent change of each stock. A regression analysis is performed to determine the correlation coefficient, and thus the strength of Twitter users' sentiment of a stock to predict its daily-trend.

<h2 align='center'>Twitter Sentiment Analysis</h2>

After the user input's their portfolio tickers, the program will retrieve up to 100 tweets per ticker symbol, created on the most recent trading-day -- excludes weekends and trading holidays -- prior to market-open (9:30am EST). The TextBlob library is used to determine the subjectivity and polarity of each stock, and the results are stored in a Pandas dataframe. 

The average subjectivity of each ticker symbol is calculated, and serves as the independent/predictor variable (x) for regression analysis. 

<h2 align='center'>Stock Portfolio Data</h2>

The yFinance library is used to retrieve Yahoo Finance data for the 'Open' and 'Close' prices of each portfolio stock on the most recent trading day. 

This data is used to calculate the daily percentage change of the stocks, which are used as the dependent variable (y) for regression analysis.

<h2 align='center'>Regression Analysis</h2>

