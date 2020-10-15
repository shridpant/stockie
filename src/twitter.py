import tweepy
import os
import sys
from textblob import TextBlob

def sentiment(api, count, keyword):
    collectedTweets = []
    tweets = api.search(keyword, count=count, tweet_mode = "extended")
    for tweet in tweets:
        blob = TextBlob(tweet.full_text)
        tweet_url = "https://twitter.com/" + tweet.user.screen_name + "/status/" + str(tweet.id)
        result = [blob.sentiment.polarity, tweet.user.name, tweet.full_text, tweet_url]
        collectedTweets.append(result) 
    return collectedTweets     

def init(keys):
    global api
    CONSUMER_KEY = keys["CONSUMER_KEY"]
    CONSUMER_SECRET = keys["CONSUMER_SECRET"]
    ACCESS_KEY = keys["ACCESS_KEY"]
    ACCESS_SECRET = keys["ACCESS_SECRET"]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    print("Twitter Bot Up for Analysis", '\n')
    return api
