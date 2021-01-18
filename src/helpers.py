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

import os
import json
import requests
import urllib.parse
from cs50 import SQL
import random

from flask import redirect, render_template, request, session
from functools import wraps

from src import meme

def UserInfo():
    db = SQL("sqlite:///src/finance.db")
    user_id_info = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
    return user_id_info

def getKeys(file_path):
    global keys
    try:
        file_opened = open("keys.json", "r")
        keys = json.load(file_opened)
        return keys
    except:
        return apology("File for keys not found")

def apology(message, code=None):
    meme.meme(message)
    return render_template("apology.html", random=random.randint(1, 32500))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def newsapi(phrase):
    url = ('http://newsapi.org/v2/top-headlines?'
        'pageSize=5&'
        'q=' + phrase + '&'
        'sortBy=popularity&'
        'apiKey=' + keys["news"])
    response = requests.get(url)
    return response.json()["articles"]


def lookup(symbol):
    # Contact API
    try:
        api_key = keys["IEX"]
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None
    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None