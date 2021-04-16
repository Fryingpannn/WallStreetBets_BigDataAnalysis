# :rocket: WallStreetBets Stock Research Posts Prediction :rocket:

***
## I. Abstract

One of the most popular platforms for stocks discussion is a subreddit called WallStreetBets. We would like to help further democratize stock trading by providing analysis and filtering on the best researches from this subreddit. This is done with the dataset consisting of the thousands of historical posts in it. As there are a lot of memes in this subreddit, we will use classification to separate the serious research posts from the joking ones, and perform predictive analysis to determine the success rate of future research posts of this subreddit.

## II. Introduction

With the influx of retail investors during the 2021 Coronavirus pandemic and GameStop short event, it is more important than ever for people to educate themselves on investment decisions. The largest financial subreddit, r/WallStreetBets, is home to many memes, however, among those joke posts, many **DD*** posts which can provide very unique insights are also present. 

Unlike professional investors, retail investors have very limited time to conduct their own research as they usually have a separate career. In this project, we aim to further democratize stock trading by using prediction and filtering on researches such that every regular investor has the opportunity to quickly access quality information and analysis. 

We will be able to provide a quick filter on the top research posts as well as provide a prediction percentage of how well a future research post may do based on historical data.

A related work is a website called SwaggyStocks.com, in which sentiment analysis of the r/WallStreetBets subreddit is done and visualized. However, we differ from this as we are not explicitly trying to analyze sentiment of the subreddit, we are only targeting the analysis the serious research posts and their corresponding stock.

***<ins>DD</ins>: Stands for "Due Diligence". Represents the investigation and research a person has done for a potential investment.**

## III. Materials and Methods

For this project, we will use two datasets. The first dataset consist of the subreddit posts, which are extracted by using the "Praw" Reddit API and Pushshift API. The Reddit API is able to provide us with many information about a given post such as the title, score, upvote ratio, author, text, URL, created time, comments and more. Except upvote ratio, score and created time, all other data are textual. 

The data labeling process require the use of another dataset. The second dataset is the stock market data from iexfinance. This dataset includes the quote, ticker, financials, cash-flow, volumes of a specific stock and more. To label data, we first need to preform some data preprocessing. 

There are many ways to analyze textual data; the Naive-Bayes classifier can be used to build a reddit post classifier. Naive-Bayes methods are a set of supervised learning algorithms based on applying Bayes' theorem with the "naive" assumption of conditional independence between every pair of features given the value of the class variable. To build the Naive-Bayes classifier, we need to extract features from the textual data from these posts. 
However, we are interested in the stock's time-series data, which is the quote (stock price) in a given time interval. We will check the stock price of the stock mentioned in a given "serious" DD, at the time the DD was posted, and at a later date. After computing the growth percentage of the difference, we will have an indication of the quality of this DD. We can then use these percentage numbers in a linear regression model to then predict the success and quality of a future DD on the subreddit.




***
