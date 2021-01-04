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
from werkzeug.utils import secure_filename
from flask import Blueprint, redirect, render_template, request
from src.helpers import apology, lookup, login_required, UserInfo

trade = Blueprint("trade", __name__, static_folder="static", template_folder="templates")
db = SQL("sqlite:///src/finance.db")

@trade.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    userInfo = UserInfo()[0]
    if request.method == "GET":
        return render_template("trade/buy.html")
    else:
        symbol = request.form.get("symbol").upper()
        number = request.form.get("number")
        if not symbol or not number or int(number)<1:
            return apology("Invalid input")
        number = int(number)
        quote = lookup(symbol)
        if quote != None:
            cost = float(number) * quote["price"]
            cash = db.execute("SELECT cash FROM users WHERE id = :id", id = userInfo["id"])[0]
            if cost > cash['cash']:
                return apology("You do not have enough cash")
            else:
                db.execute("UPDATE users SET cash = :remaining WHERE id = :id", remaining = cash['cash'] - cost, id = userInfo["id"])
                stockExists = db.execute("SELECT number FROM :username WHERE symbol=:symbol", username=userInfo['username'], symbol=symbol)
                if len(stockExists) == 0:
                    db.execute("INSERT INTO :username ('symbol', 'number') VALUES (:symbol, :number)", username=userInfo['username'], symbol = symbol, number = float(number))
                else:
                    db.execute("UPDATE :username SET number = :number WHERE symbol = :symbol", username=userInfo['username'], number = (number + int(stockExists[0]['number'])), symbol = symbol)
                db.execute("INSERT INTO :tablename ('symbol','number', 'price', 'nature') VALUES (:symbol, :number, :price, 'b')", tablename=(userInfo['username'] + "History"), symbol=symbol, number=number, price=quote['price'])
        else:
            return apology(symbol + " is an invalid symbol")
        return redirect("/")

@trade.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    userInfo = UserInfo()[0]
    if request.method == "GET":
        stock_list = db.execute("SELECT symbol FROM :username", username=userInfo['username'])
        if len(stock_list) < 1:
            return render_template("trade/sell.html")
        else:
            return render_template("trade/sell.html", stock_list=stock_list)
    else:
        stock = request.form.get("symbol")
        number = request.form.get("number")
        number_owned = db.execute("SELECT number FROM :username WHERE symbol=:symbol", username=userInfo['username'], symbol=stock)
        if not number or len(number_owned) == 0 or int(number) < 0:
            return apology("Invalid input")
        elif int(number) > number_owned[0]['number']:
            return apology("You do not own " + number + " stocks")
        number = int(number)
        quote = lookup(stock)
        cash = quote['price'] * number
        remaining = number_owned[0]['number'] - number
        if remaining != 0:
            db.execute("UPDATE :username SET number=:remaining WHERE symbol=:symbol", username=userInfo['username'], remaining=remaining, symbol=stock)
        else:
            db.execute("DELETE FROM :username WHERE symbol=:symbol", username=userInfo['username'], symbol=stock)
        db.execute("UPDATE users SET cash=:total WHERE username=:username", username=userInfo['username'], total=(cash+userInfo['cash']))
        db.execute("INSERT INTO :tablename ('symbol','number', 'price', 'nature') VALUES (:symbol, :number, :price, 's')", tablename=(userInfo['username'] + "History"), symbol=stock, number=number, price=quote['price'])
        return redirect("/")


@trade.route("/history")
@login_required
def history():
    userInfo = UserInfo()[0]
    history = db.execute("SELECT * FROM :tablename", tablename=(userInfo['username'] + "History"))
    if not history:
        return render_template("trade/history.html")
    else:
        return render_template("trade/history.html", history=history)