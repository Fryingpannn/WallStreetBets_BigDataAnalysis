# :rocket: WallStreetBets Stock Research Posts Classifier :rocket:

Project presentation: https://youtu.be/spDbteQAlbE  <br>
Project website: https://wsbrecommender.web.app/

***
# **I. Abstract**

One of the most popular platforms for stocks and financial discussion is a subreddit called WallStreetBets. We would like to help further democratize stock trading by making the access to insightful stock research easier. Most people already know about the mainstream news outlets, this is why we choose this subreddit, where insightful yet unpopularized research information lay in a sea of memes. We will use the posts on r/WallStreetBets as our dataset and aim to classify them as either valuable or less valuable in order to help any user quickly filter out posts he or she may want to read. This project aims to be particularly useful towards those, such as ourselves, who are interested in trading and investing in the stock market, but have little time to do their own research.

# **II. Introduction**

With the influx of retail investors during the 2021 Coronavirus pandemic and GameStop fiasco, it is more important now than ever for people to educate themselves on investment decisions. The largest financial subreddit, r/WallStreetBets, is home to many memes, however, many **DD*** posts are also present.

Unlike professional investors, retail investors have very limited time to conduct their own research as they usually have a separate career. In this project, we aim to further democratize stock trading by filtering and classifying stock research such that every regular investor has the opportunity to quickly access them.

We will be able to provide a quick filter on the top research posts as well as a classification on whether any given post may or may not be worth your time to read.

A related work is a website called SwaggyStocks.com, in which sentiment analysis of the r/WallStreetBets subreddit is done and visualized. However, we differ from this as we are not trying to explicitly analyze sentiment of the subreddit. Instead, we will base off our filtering upon historical performance of the stocks each post is discussing.

***DD: stands for "Due Diligence". Represents the investigation and research a person has done for a potential investment.**

# **III. Materials and Methods**

Our dataset consist of the posts from the r/WallStreetBets subreddit. They are extracted by using the Pushshift API (we previously used the Reddit PRAW API, but due to API limitations we had to revamp all our code with Pushshift instead which proved to be more flexible). The Pushshift API is able to provide us with a lot of information about a given post such as the title, score, upvote ratio, author, text, URL, created time, comments and more. Except for upvote ratio, score, created time, and number of comments, all other data are textual.

We also used the iexfinance API to obtain financial data. This API provides the closing price, ticker, financials, cash-flow, volumes of a specific ticker and more.

## Data Preprocessing

Upon receiving text data from Pushshift, we used regular expression to extract tickers from the posts. We used the iexfinance API to validate the ticker and get its closing price at the post creation date and present date. To label data, we calculated the growth percentage between these two dates. We set the standard to 6%, any post above 6% are labeled as 1 (good) else 0 (bad). We believe if whatever stock a post is talking about has risen 6%, it is worth taking a look at, plus, this number becomes crucial later in our model training step when splitting training and test sets. It allowed us to avoid data imbalance as we had a perfect split of 50% of our data as class 1 and the other 50% as class 0.

These posts are filtered and cleaned with many conditions, some of which you may see in these two functions. *(WallStreetBets-Preprocessing.ipynb)*

![image](https://user-images.githubusercontent.com/59063950/115100523-381fd900-9f0b-11eb-9fd7-a1cc39944389.png)

![image](https://user-images.githubusercontent.com/59063950/115100526-3bb36000-9f0b-11eb-9c94-431ca0c6ea91.png)

## Algorithms

To extract features, we first lemmatized the texts of each post with Spark NLP, an extension package which provides a pre-trained NLP model. we then used CountVectorizer and HashingTF from PySpark to transform textual data into vectors. CountVectorizer generates the Document-Term Matrix and contains the size of the entire vocabulary, whereas HashingTF also generates this text vector but with lower number of features (performs dimensionality reduction). 

### Naive Bayes
The first algorithm we used is Naive Bayes from PySpark's machine learning library. Naive Bayes is a supervised learning classification model based on applying Bayes' theorem. The features are the results from CountVectorizer and HashingTF. We tested with two hyperparameters, the smoothing value and the model type. The smoothing value is used to replace 0 probability event, as it makes the entire event impossible due to 1 missing feature. We also used the two most appropriate Naive Bayes model types, Complement, and Multinomial. Each model type changes the algorithm with a different method to compute the model’s coefficients, where Complement Naive Bayes is more suited for imbalanced datasets than Multinomial Naive Bayes. All these factors were randomized in many iterations to obtain the best combination.

### Clustering
The second algorithm we used is k-means++ clustering from both PySpark's machine learning library and scikit-learn, combined with PCA and TruncatedSVD/t-SNE from scikit-learn for dimensionality reduction. Because our features are vectors with thousands of dimensions (words), to visualize and plot the data we need to perform dimensionality reduction. We tested our dataset with PCA, and TruncatedSVD/t-SNE. Principal Component Analysis (PCA) maps features to an N-dimensional space, and chooses a custom number of main axis to represent the data. For PCA, the decisions of using which axis is based on the minimized square distances between the data points and the axis, whereas t-SNE uses the probability of neighboring points, and computes the best components to represent that probability. 

# IV. Results

## Naive Bayes
As previously noted, the label we used to train our Naive Bayes classifier is the growth percentage of a stock associated with a given reddit post, with the instances being the text of each post. 

With this, our best model achieved an accuracy of 64.91%. This was obtained by choosing CountVectorizer to vectorize our features, using Multinomial Naive Bayes and a smoothing parameter of 0.2684835. This model had an F1 score of 0.65, precision of 0.58 and recall of 0.73.

In the following table, you may observe the top 10 results we obtained from over one hundred iterations of changing the parameters and training/test sets while training Naive Bayes models, with both the CountVectorizer and HashingTF methods.

![image](https://user-images.githubusercontent.com/59063950/115100544-538ae400-9f0b-11eb-928a-8db23119abd4.png)

![image](https://user-images.githubusercontent.com/59063950/115100549-584f9800-9f0b-11eb-91b8-63a991b2f7f1.png)

For HashingTF, we used 50 as the 'number of features' hyperparameter (default is 20). This essentially causes dimensionality reduction on each of our instances, which may be why the overall accuracy mean is lower than CountVectorizer as less features are considered during training, leading to loss of information.

It also seems that the model type, whether multinomial or complement, lead to similar results. In theory, complement Naive Bayes works better on imbalanced datasets than multinomial Naive Bayes. Although our dataset is balanced as both classes are split 50/50, the features themselves of each instance may not be balanced as a lot of posts are talking about the same stock: GME. We suspect this may be the reason why both model types have similar results.

## Clustering

For clustering, it was difficult to see the differences in clusters. Although we performed many iterations while changing different parameters, the results from PySpark were similar. Here's an example obtained with k-means++. Most of our results looked like this whether we used t-SNE/TruncateSVD or PCA for dimensionality reduction.

![image](https://user-images.githubusercontent.com/59063950/115100562-6ac9d180-9f0b-11eb-8722-b949ffdf24c8.png)

We later pre-processed the data again using SparkNLP to lemmatize the texts. We then used scikit-learn to cluster the data again with t-SNE and k-means++. Here are examples of our results with 2, 3 and 4 clusters. Each color is a different cluster, with the red line indicating the average silhouette coefficient value.

![image](https://user-images.githubusercontent.com/59063950/115100567-774e2a00-9f0b-11eb-98e3-50296c9c61d2.png)
![image](https://user-images.githubusercontent.com/59063950/115100569-7ddca180-9f0b-11eb-88af-1a85a0b947e2.png)
![image](https://user-images.githubusercontent.com/59063950/115100573-82a15580-9f0b-11eb-8d84-82e16e88814d.png)

With scikit-learn, we were able to better visualize our results and perceive differences in clusters, this may be in part due to the added lemmatization process. However, as we increase the number of clusters, we see that the cluster separations remain almost constant. This leads us to believe there isn't actually much separation between our data points, which is consistent with our visualizations from PySpark clustering, but also consistent with the 65% accuracy result from our Naive Bayes model, which isn't very high, but enough to be interesting.

In the next section, we shall discuss the relevance of our solutions and possible future work.

# Discussion

Numerically, with 65% accuracy, our Naive Bayes model doesn't seem tremendously "accurate" or "precise". However, it must be noted that the goal of this classifier is simply to indicate which posts has a higher chance of being worth the user's time to read. Remember that this result is also obtained after having already filtered the posts with many variables as previously mentioned, thus the final classified posts actually have very good chances to be worth a read.

## Potential Issues

1. Bias
    - In the data we used to train our Naive Bayes classifier, a lot of the posts were discussing about the same stock, GME. This can cause some degree of bias as the words in those posts have a higher chance to relate to each other.
    - Although our ticker extraction algorithm is very accurate, sometimes the ticker identified for a given post is still inaccurate. This can also cause bias as then the computed growth percentage (label) would not be relevant for the associated post.
2. Lack of data
    - From around 40 000 posts, we filtered and cleaned it down to 1141 data points. Although these remaining 1141 posts we used to train the model were of good quality due to all the filtering we did, it is still a small quantity. We believe we may get even better results by acquiring more data, which was very difficult due to API limitations.

## Closing thoughts

As for utility, we believe our solution, with just a bit more tuning, can actually be useful and create value. In the goal of making access to stock research easier, we plan to create a website, on which many features would be present. This Naive Bayes classifier can easily be one of the features: by displaying a list of filtered research posts, we may indicate beside each of them, the probability that they would be worth a read.

We believe this would be of great interest to those, such as ourselves, who like trading and investing in the stock market, but have little time to find and do research of their own.

In conclusion, this project was incredibly interesting for us. We had the chance to go through essentially the whole data science workflow, from finding a unique problem statement, gathering data, training models and presenting, as well as somewhat accomplish our goal to create something useful. As undergraduate students, it was a tremendous learning experience and we hope to create more exciting projects like this one.

***
