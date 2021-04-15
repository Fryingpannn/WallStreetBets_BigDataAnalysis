from pyspark.rdd import RDD
from pyspark.sql import Row
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
import os
import re
import math
import json
import requests
import itertools
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
import string
import holidays
from iexfinance.account import get_metadata


ticker_set=set()
backupkey = ''
def sandbox(change):
  if change:
    # Set IEX Finance API Token for Sandbox test mode
    os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
    os.environ['IEX_TOKEN'] = ''
  else:
    # Real
    os.environ['IEX_API_VERSION'] = 'stable'
    os.environ['IEX_TOKEN'] = ''

sandbox(False)

def get_start_date(created):
  # 1 day before post date
  us_holidays = holidays.UnitedStates(years = 2021)+holidays.UnitedStates(years=2020)
  ticker_date = datetime.fromtimestamp(int(created) - 86400).date()

  if ticker_date in us_holidays or ticker_date == datetime(2021, 4, 2).date():
    return False
  if ticker_date.weekday() in [5,6]:
    return False
  
  return ticker_date

def init_spark():
    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()
    return spark

# helper function for get_ticker, extracts ticker after dollar signs if exists
def check_after_dollarsign(body, start_index):
   """
   Given a starting index and text, this will extract the ticker, return None if it is incorrectly formatted.
   """
   count  = 0
   ticker = ""

   for char in body[start_index:]:
      # if it should return
      if not char.isalpha():
         # if there aren't any letters following the $
         if (count == 0):
            return None

         return ticker.upper()
      else:
         ticker += char
         count += 1

   return ticker.upper()

# function to retrieve ticker from a body of text
def get_ticker(body):
   global ticker_set
   # frequent words that look like tickers but aren't
   blacklist_words = [
      "YOLO", "TOS", "CEO", "CFO", "CTO", "DD", "BTFD", "WSB", "OK", "RH",
      "KYS", "FD", "TYS", "US", "USA", "IT", "ATH", "RIP", "BMW", "GDP",
      "OTM", "ATM", "ITM", "IMO", "LOL", "DOJ", "BE", "PR", "PC", "ICE",
      "TYS", "ISIS", "PRAY", "PT", "FBI", "SEC", "GOD", "NOT", "POS", "COD",
      "AYYMD", "FOMO", "TL;DR", "EDIT", "STILL", "LGMA", "WTF", "RAW", "PM",
      "LMAO", "LMFAO", "ROFL", "EZ", "RED", "BEZOS", "TICK", "IS", "DOW"
      "AM", "PM", "LPT", "GOAT", "FL", "CA", "IL", "PDFUA", "MACD", "HQ",
      "OP", "DJIA", "PS", "AH", "TL", "DR", "JAN", "FEB", "JUL", "AUG",
      "SEP", "SEPT", "OCT", "NOV", "DEC", "FDA", "IV", "ER", "IPO", "RISE"
      "IPA", "URL", "MILF", "BUT", "SSN", "FIFA", "USD", "CPU", "AT",
      "GG", "ELON", "I", "WE", "A", "AND","THE","THIS","TO","BUY","MY","MOST","ARK",
      "IN","S","BABY","APES"
   ]

   # FIRST CHECK IF THERE'S A $TICKER WITH DOLLAR SIGN
   if '$' in body:
      index = body.find('$') + 1
      word = check_after_dollarsign(body, index)
      
      if word and word not in blacklist_words:
         try:
            # special case for $ROPE
            if word != "ROPE":
               # sends request to IEX API to determine whether the current word is a valid ticker
               # if it isn't, it'll return an error and therefore continue on to the next word
               if not word in ticker_set:
                  price = Stock(word).get_company()
                  ticker_set.add(word)
               else:
                  return word
         except Exception as e:
            pass
   
   # IF NO TICKER WITH DOLLAR SIGN, CHECK FOR TICKER WITHOUT IT: splits every body into list of words
   word_list = re.sub("[^\w]", " ",  body).split()
   for count, word in enumerate(word_list):
      # initial screening of words
      if word.isupper() and len(word) >= 1 and (word.upper() not in blacklist_words) and len(word) <= 5 and word.isalpha():
         try:
            # special case for $ROPE
            if word != "ROPE":
               if not word in ticker_set:
                  price = Stock(word).get_company()
                  ticker_set.add(word)
               else:
                  return word
         except Exception as e: 
            continue
      
   # if no ticker was found
   return "None"

get_attempts = 0
'''
Compute growth % of associated stock in a given post.
'''
# computes growth % of given DD
# (today's price <> price at DD's date) = percentage growth from then to now of the stock
def growth(ticker, created):
    if not ticker or ticker == "None":
        return "N/A"
    # get today's date and DD's date (ranges from <>1 week in case of weekends/holidays)
    try:
        # get today's price
        sandbox(True)
        price_today = Stock(ticker).get_quote().latestPrice[ticker]

        ticker_date_start = get_start_date(created)
        ticker_date_end = datetime.fromtimestamp(int(created))

        # dates for post creation: loop until get valid date
        counter = 0
        new_date = created
        while not ticker_date_start and counter < 20:
          counter += 1
          new_date -= 86400
          ticker_date_start = get_start_date(new_date)
        # get DD date's price
        if ticker_date_start:
          ticker_date_end = ticker_date_start + timedelta(days=0.8)
          price_ticker_date = get_historical_data(ticker, ticker_date_start, ticker_date_end, close_only=True).close[0]

        # compute percentage growth
        #print(ticker,created)
        #print(get_metadata())
        percentage = ((price_today / price_ticker_date) - 1) * 100
        return "{:.2f}".format(percentage) + "%"
    except Exception as e:
        print(e)
        return "N/A"

def get_request(uri, max_retry = 5):

  def get(uri):
    global get_attempts
    global sesh
    get_attempts += 1
    #time.sleep(1)
    response = sesh.get(uri, timeout=20)
    assert response.status_code == 200
    return json.loads(response.content)
  # Retry if request call failed
  retry = 1
  while retry < max_retry:
    try:
      response = get(uri)
      return response
    except Exception as e:
      if 'timed out' in str(e):
        print("Retry " + str(retry)+ " Timed out. Request #" + str(get_attempts))
      retry += 1

def clean_text(text):
  # remove punctuation except $
  cleaned = text.translate(str.maketrans(' ', ' ', string.punctuation.replace('$','') + '’')).lower()
  # remove links (http)
  cleaned = re.sub("http\w+", " ", cleaned)
  # remove digits
  cleaned = cleaned.translate({ord(k): None for k in string.digits})
  # remove tabs/newlines
  cleaned = cleaned.replace("\n", " ").replace("\t", " ").strip()
  # remove double space
  cleaned = re.sub(' +', ' ', cleaned)
  return cleaned

def validate_post(post):
  return (post['link_flair_text']
          and post['upvote_ratio'] > 0.2
    and post['link_flair_css_class']
    and post['selftext']
    and not post['selftext'].isspace()
    and post['selftext'] != "removed"
    and post['selftext'] != "[removed]"
    and post['selftext'] != "[deleted]")

def get_posts(subreddit, begin, end):
  # Max size of each Pushshift API request is 100 posts.
  SIZE = 100
  #'https://api.pushshift.io/reddit/search/submission?subreddit=wallstreetbets&score=>5&size=25&selftext:not="preview.redd.it"&fields=id,created_utc,title,score,upvote_ratio,author,link_flair_text,link_flair_css_class,num_comments,selftext,url'
  PUSHSHIFT_URI = r'https://api.pushshift.io/reddit/search/submission?subreddit={}&after={}&before={}&size={}&is_video=false&fields=total_awards_received,id,created_utc,title,score,upvote_ratio,author,link_flair_text,link_flair_css_class,num_comments,selftext,url'
  nb_requests_made = 1
  # filter the posts data
  def filter_posts(uri, begin, end):
    full_posts = get_request(uri.format(subreddit, begin, end, SIZE))
    #if full_posts is None:
      #raise ValueError("Response is empty or none.")
    posts = []
    if full_posts!=None:
      for post in full_posts['data']:
        try:
          if validate_post(post):
            sandbox(True)
            ticker =  get_ticker(post['title'])
            sandbox(False)
            posts.append({\
              'id': post['id'],\
              'ticker': ticker, \
              'growth': growth(ticker, post['created_utc']),\
              'title': clean_text(post['title']),\
              'score': post['score'],\
              'upvote_ratio': post['upvote_ratio'],\
              'author': post['author'],\
              'created_utc': post['created_utc'],\
              'flair': post['link_flair_text'],\
              'flaircss': post['link_flair_css_class'],\
              'num_comments': post['num_comments'],\
              'text': clean_text(post['selftext']),\
              'total_awards': post['total_awards_received'],\
              'url': post['url']\
            })
        except:
          pass
      # get timestamp of last post
      #print(full_posts['data'][0]["score"])
      last_timestamp = full_posts['data'][-1]['created_utc']
      posts_amount = len(full_posts['data'])
          
      #return list(filtered)
      return [posts, last_timestamp, posts_amount]
    else:
      return None 
  posts_etc = filter_posts(PUSHSHIFT_URI, begin, end)
  posts = posts_etc[0]
  last_timestamp = posts_etc[1]
  posts_amount = posts_etc[2]

  # If reached limit of 100 posts retrieved, make request again until 'end' time.
  while posts_amount == SIZE:
    
    # Timestamp of the last post we previously retrieved
    new_begin = last_timestamp - 10
    more_posts_etc = filter_posts(PUSHSHIFT_URI, new_begin, end)
    if more_posts_etc==None:
      time.sleep(1)
      last_timestamp+=10
      print("sleep")
    else:
      last_timestamp = more_posts_etc[1]
      posts_amount = more_posts_etc[2]
      posts.extend(more_posts_etc[0])
      nb_requests_made += 1
      print(new_begin,end)
    
  print("Number of requests made: ", nb_requests_made)
  return posts

"""
Retrieve posts
- nb_days_from_today: number of days from today you want to retrieve
- return: lists of all posts in time interval
"""
get_attempts = 0
def retrieve(nb_days_from_today):
  global get_attempts
  end = math.ceil(datetime.utcnow().timestamp()-345600)
  if nb_days_from_today < 3650:
    begin = math.ceil((datetime.fromtimestamp(end) - timedelta(days=nb_days_from_today)).timestamp())
  else:
    begin = nb_days_from_today
  print("Timestamps: ", begin, end)
  posts = get_posts('wallstreetbets', begin, end)

  unique_posts = np.unique([post['id'] for post in posts])
  print("Size: ", len(posts))
  print("Size of uniques: ", len(unique_posts))
  print("Example posts: ", posts[:5])
  print("Total requests: " + str(get_attempts))
  return posts

def convert_to_date(timestamp):
  return str(datetime.fromtimestamp(int(timestamp)).date())

# all posts!
#70 days


if __name__ == '__main__':

  """
  os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
  os.environ['IEX_TOKEN'] = 'Tsk_66e4f6e5f10e45cd9d7caa1a487297dd'
  """
  sesh = requests.Session()
  days=100
  posts = retrieve(days)
  print(len(posts))
  spark = init_spark()
  posts_rdd = spark.sparkContext.parallelize(posts)
  posts_rdd = posts_rdd.map(lambda post: Row(id=post['id'], ticker=post['ticker'], growth=post['growth'], title=post['title'], flair=str(post['flair']), score=post['score'], upvote_ratio=post['upvote_ratio'], author=str(post['author']), num_comments=post['num_comments'], text=post['text'].lower(), created=convert_to_date(post['created_utc']), url=post['url']))
  # eliminate duplicates
  posts_rdd = posts_rdd.distinct()
  posts_df = spark.createDataFrame(posts_rdd)
  print(posts_df.count())
  panda_posts = posts_df.toPandas()

  # write to csv
  posts_df.coalesce(1).write.csv(str(days)+'days.csv', header=True)
  #panda_posts
  #obj2 = get_request('https://api.pushshift.io/reddit/search/submission?subreddit=wallstreetbets&score=>4&selftext:not="[removed]"&is_video=false&size=25&fields=id,created_utc,title,score,upvote_ratio,author,link_flair_text,link_flair_css_class,num_comments,selftext,url')
  

