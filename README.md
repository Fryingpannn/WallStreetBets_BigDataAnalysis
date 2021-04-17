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

For this project, our dataset consist of the subreddit posts, which are extracted by using the "Praw" Reddit API and Pushshift API. The Reddit API is able to provide us with many information about a given post such as the title, score, upvote ratio, author, text, URL, created time, comments and more. Except for upvote ratio, score and created time, all other data are textual.

We also used the iexfinance API to get the stock market data. This API provides the closing price, ticker, financials, cash-flow, volumes of a specific ticker and more.

The data preprocessing includes the data labeling and feature extractions from textual data. Upon receiving text data from Pushshift, we used regular expression to extract tickers from posts if there exists any. We used iexfinance API to validate the ticker and get the closing price of that ticker at the post creation date and present. To label data, we calculated the growth percentage . We set the standard to 6%, any percentage above are labeled as 1 otherwise 0. To extract features, we first cleaned the text data in the post with Spark NLP, an extension package which provides a trained NLP model to perform lemmatization. we used CountVectorizer and HashingTF from PySpark to transform textual data into vectors. CountVectorizer generates sparse matrix with the size of vocabulary, and HashingTF generates a hashing table with lower number of features. 

The algorithm we used is Naive Bayes from PySpark. Naive Bayes is a supervised learning classification model  based on applying Bayes' theorem with the "naive" assumption of conditional independence between every pair of features given the value of the class variable. The features are the results from CountVectorizer and HashingTF. We tested with two hyperparameters, the smoothing value and the model type. The smoothing value is used to replace 0 probability event, as it makes the entire event impossible due to 1 missing feature. There are two model types to test, Complement, and Multinomial. Each model type changes the algorithm with different method to compute model’s coefficients.

The second algorithms we used is KMeans clustering from PySpark, combine with PCA, truncatedSVD and T-SNE from scikit-learn for data visualization. Because our features is a vectors with 1000s of dimensions (words), to visualize and plot the data we need to do dimensionality reduction. We tested our dataset with PCA, and truncatedSVD + T-Sne. Principal Component Analysis map features to N-dimensional space, and chose custom number of main axis to represent data. The decisions of using which axis is based on the minimized square distance between the datapoint and the axis. However, T-SNE used the probability of neighboring points, and compute the best components to represent that probability.




***
