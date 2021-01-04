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

from flask import Blueprint, redirect, render_template, request
from src.helpers import apology, login_required, getKeys, newsapi
from src import twitter
from src.performance import PreInfo, Information, Sustainability

insights = Blueprint("insights", __name__, static_folder="static", template_folder="templates")
# Make sure API key is set
keys = getKeys("key.json")

@insights.route("/", defaults = {'stock_symbol': None}, methods = ["GET", "POST"])
@insights.route("/<stock_symbol>/", methods = ["GET", "POST"])
@login_required
def landing(stock_symbol = None):
    # GET Request Handling
    if request.method == "GET":
        if stock_symbol != None:
            informationInsights = Information(stock_symbol)
            if informationInsights != None:
                open_df = informationInsights[1]["Open"].tolist()
                close_df = informationInsights[1]["Close"].tolist()
                high_df = informationInsights[1]["High"].tolist()
                low_df = informationInsights[1]["Low"].tolist()
                return render_template("insights/insights.html", method="POST", display="company", info=informationInsights, open=open_df, close=close_df, high=high_df, low=low_df)
            else:
                return apology("Not found", 404)
        else: 
            return render_template("insights/insights.html", method="GET")
    # POST Request Handling
    else:
        search_phrase = request.form.get("phrase")
        stock_symbol = request.form.get("symbol")
        if stock_symbol:
            return redirect("/insights/" + stock_symbol)
        elif search_phrase:
            #TODO Better analysis methods
            try:
                # Connect to Twitter
                twitterAPI = twitter.init(keys)
                yfinanceInsights = PreInfo(search_phrase)
                if yfinanceInsights != None:
                    search_phrase = yfinanceInsights[0]["shortName"]
                tweetInsights = twitter.sentiment(twitterAPI, 7, search_phrase)
                newsInsights = newsapi(search_phrase)
                if len(tweetInsights) == 0 and len(newsInsights) == 0:
                    return render_template("insights/insights.html", method="POST", display="nlp", search_phrase=search_phrase, company = yfinanceInsights)
                elif len(tweetInsights) == 0:
                    return render_template("insights/insights.html", method="POST", display="nlp", news=newsInsights, search_phrase=search_phrase, company = yfinanceInsights)
                elif len(newsInsights) == 0:
                    return render_template("insights/insights.html", method = "POST", display="nlp", tweets = tweetInsights, search_phrase=search_phrase, company = yfinanceInsights)
                else:
                    return render_template("insights/insights.html", method = "POST", display="nlp", tweets = tweetInsights, news=newsInsights, company = yfinanceInsights)
            except Exception as inst:
                return apology(str(inst))
        else:
            return apology("Unknown error")
