import praw # connect to Reddit API (python reddit api wrapper)
import pandas as pd # handle, format export data
import datetime as dt # convert unix timestamp
import time as time # get unix timestamp
import re
from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
import os


# connecting to reddit API
def connect_reddit():
    # connect to reddit and store in a variable with praw.Reddit()
    # client id used for reddit to identify my app, used with secret to get access token (OAuth)
    key_file= open("secret.txt","r")
    setting=dict()
    for i in key_file:
        if("secret" in i):
            setting["secret"]=i.split("=")[1].strip()
        elif("user_agent" in i):
            setting["user_agent"]=i.split("=")[1].strip()
        elif("clientid" in i):
            setting["clientid"]=i.split("=")[1].strip()
        elif("iexf_pub" in i):
            setting["iexf_pub"]=i.split("=")[1].strip()
        elif("iexf_sec" in i):
            setting["iexf_sec"]=i.split("=")[1].strip()

    key_file.close()
    print(setting)
    r = praw.Reddit(client_id=setting["clientid"], \
        client_secret=setting["secret"], \
        user_agent=setting["user_agent"]
        )

    # to retrieve subreddit, pass in the sub's name
    newr = r.subreddit('wallstreetbets')

    # each subreddit separated in diff topics, such as top, hot, etc.
    # -> grabbing recent 1000 posts (limit = latest X nb of posts):
    top_subreddit = newr.new(limit=None)

    return top_subreddit

# stores data in a dataframe; returns the dataframe object
def store_data(top_subreddit):
    # dictionary to hold the attributes of each hot post/submission of the subreddit
    
    top_info = {
              #"ticker" : [],
               "title" : [], 
               "score" : [], 
               "upvote_ratio" : [], 
               "author" : [], 
               "text" : [],
               #"growth" : [],
               "url" : [],
               "created" : []}
    
    #top_info=dict()
    # adding the attributes of the hot posts to the dictionary
    for posts in top_subreddit:
         # only add if it's a DD
        if(posts.link_flair_text == "DD"):
                top_info["url"].append(posts.url)
                top_info["title"].append(posts.title)
                top_info["score"].append(posts.score)
                top_info["upvote_ratio"].append(posts.upvote_ratio)
                top_info["author"].append(posts.author)
                top_info["text"].append(posts.selftext)
                top_info["created"].append(posts.created)
                
            """
            ticker = get_ticker(posts.title)
            top_info["ticker"].append(ticker)
            """
            #top_info["growth"].append(growth(ticker, posts.created))

    # converting dictionary to dataframe table for illustration
    for key in top_info:
        print(key,len(top_info[key]))
    top_data = pd.DataFrame(top_info)

    # applies the get_date() function on all values of created column, returns new column
    #_timestamp = top_data["created"].apply(get_date)
    # append human readable date to 'created' column
    #top_data = top_data.assign(created = _timestamp)
    return top_data

# function to retrieve ticker from a body of text
def get_ticker(body):
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
      "GG", "ELON"
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
               price = Stock(word).get_company()
               return word
         except Exception as e:
            print("[Skipped one post]")
            print(e)
            pass
   
   # IF NO TICKER WITH DOLLAR SIGN, CHECK FOR TICKER WITHOUT IT: splits every body into list of words
   word_list = re.sub("[^\w]", " ",  body).split()
   for count, word in enumerate(word_list):
      # initial screening of words
      if word.isupper() and len(word) >= 1 and (word.upper() not in blacklist_words) and len(word) <= 5 and word.isalpha():
         try:
            # special case for $ROPE
            if word != "ROPE":
               price = Stock(word).get_company()
               return word
         except Exception as e: 
            print("[Skipped one post]")
            print(e)
            continue
      
   # if no ticker was found
   return None

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

def growth(ticker, created):
    if ticker is None:
        return None
    # get today's date and DD's date (ranges from <>1 week in case of weekends/holidays)
    try:
        today = get_date(time.time() - 604800)
        today_end = dt.date.today()
        ticker_date = get_date(created - 604800)
        ticker_date_end = get_date(created)
        # get today's price and DD date's price
        price_today = get_historical_data(ticker, today, today_end, close_only=True)
        price_today = price_today.close[len(price_today.close)-1] # get latest price for end date
        price_ticker_date = get_historical_data(ticker, ticker_date, ticker_date_end, close_only=True).close[0]
        # compute percentage growth
        percentage = ((price_today / price_ticker_date) - 1) * 100
        return percentage
    except Exception as e:
        print("==== Error in growth() function ====")
        print(e)
        return None

if __name__ == '__main__':
    a=connect_reddit()
    dataframe = store_data(a)
    dataframe.to_csv("results_v2.csv")

