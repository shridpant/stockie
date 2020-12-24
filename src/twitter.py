# MIT License

# Copyright (c) 2020 Shrid Pant

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
