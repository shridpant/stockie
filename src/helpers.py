import os
import json
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def getKeys(file_path):
    global keys
    try:
        file_opened = open("keys.json", "r")
    except:
        return apology("File for keys not found")
    keys = json.load(file_opened)
    return keys

def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


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


def usd(value):
    return f"${value:,.2f}"
