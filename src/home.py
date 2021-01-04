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

from cs50 import SQL
from werkzeug.security import check_password_hash
from flask import Blueprint, redirect, render_template, request, session
from src.helpers import apology, login_required, getKeys, UserInfo, lookup

home = Blueprint("home", __name__, static_folder="static", template_folder="templates")
db = SQL("sqlite:///src/finance.db")
keys = getKeys("key.json")

@home.route("/", methods=["GET", "POST"])
@home.route("/home", methods=["GET", "POST"])
@login_required
def index():
    userInfo = UserInfo()[0]
    # Get Relevant Information
    stocks = db.execute("SELECT * FROM :username", username = userInfo['username'])
    price = {}
    wealth = userInfo['cash']
    for stock in stocks:
        price[stock["symbol"]] = lookup(stock["symbol"])['price']
        wealth += price[stock["symbol"]] * stock["number"]
    db.execute("UPDATE users SET wealth = :wealth WHERE id = :id", wealth = wealth, id = session["user_id"])
    cash = "{:.2f}".format(userInfo['cash'])
    wealth = "{:.2f}".format(wealth)
    # GET Request Handling
    if request.method == "GET":
        if not stocks:
            return render_template("index.html", method = "GET", cash = cash, wealth = wealth)
        else:
            return render_template("index.html", method = "GET", stocks = stocks, price = price, cash = cash, wealth = wealth)
    # POST Reuqest Handling
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("You must provide a symbol")
        quote = lookup(symbol)
        if quote != None:
            if not stocks:
                return render_template("index.html", method="POST", cash = cash, wealth = wealth, quote = quote)
            else:
                return render_template("index.html", method="POST", stocks=stocks, price=price, cash = cash, wealth = wealth, quote = quote)
        else:
            return apology(symbol + " is an invalid symbol")

@home.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    # POST Request Handling
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("You must provide username", 403)
        elif not request.form.get("password"):
            return apology("You must provide password", 403)
        accountExists = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(accountExists) != 1 or not check_password_hash(accountExists[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)
        session["user_id"] = accountExists[0]["id"]
        return redirect("/")
    # GET Request Handling
    else:
        return render_template("auth/login.html")

@home.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
