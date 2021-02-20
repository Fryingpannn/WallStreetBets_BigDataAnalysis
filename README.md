# WallStreetBets Stock Research Posts Prediction

***

More than ever, stock trading has become democratized to retail investors. One of the most popular platforms for discussion is a subreddit called WallStreetBets. Unlike professional investors, retail investors have very limited time to conduct their own research as they usually have a separate career. In this project, we aim to further democratize stock trading by using prediction and filtering on research so that every regular investor has the opportunity to quickly access quality information and analysis.

The dataset we will use are the reddit posts categorized as “DD” (Due Diligence), which are stock research on WallStreetBets. We will collect this data by using the Reddit API and use classification to separate the serious research posts from the meme posts by tokenizing the content with Bag-of-words method and by applying Naive-Bayes method. We will then check the stock growth of a stock corresponding to a given serious post repeatedly, in a given time interval, and use this data to make a prediction on future research posts of this subreddit.

***

## I. Introduction

## II. Materials and Methods
For this project, we will use two datasets.   
The first dataset is the subReddit post/submission from Reddit, which is extracted by using "praw" API and pushshift API.  
The Reddit dataset has 9 columns of data: title,score,upvote_ratio,author,text,url,created(timestamp), comments and link flair text (tags). Except upvote_ratio and created(timestamp), all datas are textual data. There are many ways to analyze textual data, Naive-Bayes method can be used to build a Reddit-post classifer. To build the Naive-Bayes classifier, we need to split the posts into significant posts and less significant posts. We can first use the posts' tags to identify them (tag of DD). We will also need to extract features from the textual data from these posts, one of the way is tokenize all the english words in the text, count their frequencies and compare it to other posts.

The second dataset is the stock market data from iexfinance. This dataset includes quote, stats, financials, cash-flow of a specific stock. However, we are interested in the time series data of the stocks to evaluate the effects and its consequence that it brings to the stock. 

Matthew Pan (40135588)<br>
Ling Zhi Mo (40024810)
