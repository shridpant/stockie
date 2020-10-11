# todo- Cleanup

import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
os.environ["API_KEY"] = 'pk_dcf82be1ea1943379f77782df104d6d8'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id_info = db.execute("SELECT username, cash, wealth FROM users WHERE id = :id", id = session["user_id"])
    stocks = db.execute("SELECT * FROM :username", username=user_id_info[0]['username'])
    price = {}
    wealth = user_id_info[0]['cash']
    for stock in stocks:
        price[stock["symbol"]] = lookup(stock["symbol"])['price']
        wealth += price[stock["symbol"]] * stock["number"]
    db.execute("UPDATE users SET wealth = :wealth WHERE id = :id", wealth=wealth, id = session["user_id"])
    cash = "{:.2f}".format(user_id_info[0]['cash'])
    wealth = "{:.2f}".format(wealth)
    return render_template("index.html", stocks=stocks, price=price, cash = cash, wealth = wealth)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    user_id_info = db.execute("SELECT username, cash, wealth FROM users WHERE id = :id", id = session["user_id"])
    if request.method == "GET":
        return render_template("buy.html")
    elif request.method == "POST":
        symbol = request.form.get("symbol")
        number = int(request.form.get("number"))
        if not symbol:
            return apology("You must provide a symbol")
        quote = lookup(symbol)
        if quote != None:
            cost = float(number) * quote["price"]
            cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
            if cost > cash[0]['cash']:
                return apology("You do not have enough cash")
            else:
                db.execute("UPDATE users SET cash = :remaining WHERE id = :id", remaining = cash[0]['cash'] - cost, id = session["user_id"])
                existence = db.execute("SELECT number FROM :username WHERE symbol=:symbol", username=user_id_info[0]['username'], symbol=symbol)
                # Query database for username
                username = db.execute("SELECT username FROM users WHERE id = :id", id = session["user_id"])
                if len(existence) == 0:
                    db.execute("INSERT INTO :username ('symbol', 'number') VALUES (:symbol, :number)", username=username[0]['username'], symbol = symbol, number = float(number))
                elif len(existence) == 1:
                    db.execute("UPDATE :username SET number = :number WHERE symbol = :symbol", username=username[0]['username'], number = number+int(existence[0]['number']), symbol = symbol)
                else:
                    pass
                tablename = user_id_info[0]['username'] + "History"
                db.execute("INSERT INTO :tablename ('symbol','number', 'price') VALUES (:symbol, :number, :price)", tablename=tablename, symbol=symbol, number=number, price=quote['price'])
        else:
            apology_message = symbol + " is an invalid symbol"
            return apology(apology_message)
        return redirect("/")
    else:
        pass

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id_info = db.execute("SELECT username, cash, wealth FROM users WHERE id = :id", id = session["user_id"])
    tablename = user_id_info[0]['username'] + "History"
    history = db.execute("SELECT * FROM :tablename", tablename=tablename)
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("You must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("You must provide password", 403)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html", method="GET")
    elif request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("You must provide a sumbol")
        quote = lookup(symbol)
        if quote != None:
            return render_template("quote.html", method="POST", quote=quote)
        else:
            apology_message = symbol + " is an invalid symbol"
            return apology(apology_message)

@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")
    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        # Ensure username was submitted
        if not username:
            return apology("You must provide a username")
        # Ensure password was submitted
        elif not password:
            return apology("You must provide a password")
        # Ensure the passwords match
        elif password != confirm:
            return apology("Your passwords do not match")
        # Insert the username and hash onto the SQL database
        try:
            tablename = username+"History"
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=generate_password_hash(password))
            db.execute("CREATE TABLE IF NOT EXISTS :username ('symbol' TEXT NOT NULL PRIMARY KEY, 'number' NUMERIC NOT NULL)", username=username)
            db.execute("CREATE TABLE IF NOT EXISTS :tablename ('transaction' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'symbol' TEXT NOT NULL,'number' NUMERIC NOT NULL, 'price' NUMERIC NOT NULL, 'timestamp' DATETIME DEFAULT CURRENT_TIMESTAMP)", tablename=tablename)
            return redirect("/")
        # Check for error
        except Exception as inst:
            if "unique constraint failed" in str(inst).lower():
                return apology("Username already taken")
            else:
                return apology(str(inst))

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id_info = db.execute("SELECT username, cash, wealth FROM users WHERE id = :id", id = session["user_id"])
    if request.method == "GET":
        stock_list = db.execute("SELECT symbol FROM :username", username=user_id_info[0]['username'])
        return render_template("sell.html", stock_list=stock_list)
    elif request.method == "POST":
        stock = request.form.get("symbol")
        number = int(request.form.get("number"))
        number_owned = db.execute("SELECT number FROM :username WHERE symbol=:symbol", username=user_id_info[0]['username'], symbol=stock)
        if not number:
            return apology("You must provide a symbol")
        elif number > number_owned[0]['number']:
            return apology("You do not own " + str(number) + " stocks")
        quote = lookup(stock)
        cash = quote['price'] * number
        remaining = number_owned[0]['number'] - number
        if remaining != 0:
            db.execute("UPDATE :username SET number=:remaining WHERE symbol=:symbol", username=user_id_info[0]['username'], remaining =remaining, symbol=stock)
        else:
            db.execute("DELETE FROM :username WHERE symbol=:symbol", username=user_id_info[0]['username'], symbol=stock)
        db.execute("UPDATE users SET cash=:total WHERE username=:username", username=user_id_info[0]['username'], total=cash+user_id_info[0]['cash'])
        tablename = user_id_info[0]['username'] + "History"
        db.execute("INSERT INTO :tablename ('symbol','number', 'price') VALUES (:symbol, :number, :price)", tablename=tablename, symbol=stock, number=number, price=quote['price'])
        return redirect("/")
    else:
        pass

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=True)
