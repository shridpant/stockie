import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_socketio import SocketIO, send, emit
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.utils import secure_filename
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from src.helpers import newsapi, apology, login_required, lookup, usd, getKeys
from src import twitter

# Configure application
app = Flask(__name__)
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
# Secret key for chat
app.config["SECRET_KEY"] = "secretkey"
# SocketIO
socketio = SocketIO(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
# Make sure API key is set
keys = getKeys("key.json")
# Connect to Twitter
twitterAPI = twitter.init(keys)

def UserInfo():
    user_id_info = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
    return user_id_info

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    userInfo = UserInfo()[0]
    # Get Initial Information
    stocks = db.execute("SELECT * FROM :username", username=userInfo['username'])
    price = {}
    wealth = userInfo['cash']
    for stock in stocks:
        price[stock["symbol"]] = lookup(stock["symbol"])['price']
        wealth += price[stock["symbol"]] * stock["number"]
    db.execute("UPDATE users SET wealth = :wealth WHERE id = :id", wealth=wealth, id = session["user_id"])
    cash = "{:.2f}".format(userInfo['cash'])
    wealth = "{:.2f}".format(wealth)
    if request.method == "GET":
        if not stocks:
            return render_template("index.html", method="GET", cash = cash, wealth = wealth)
        else:
            return render_template("index.html", method="GET", stocks=stocks, price=price, cash = cash, wealth = wealth)
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

@app.route("/insights", methods=["GET", "POST"])
@login_required
def insights():
    if request.method == "GET":
        return render_template("insights.html", method="GET")
    else:
        search_phrase = request.form.get("phrase")
        if not search_phrase:
            return apology("You must enter a search phrase")
        else:
            #TODO Better analysis methods
            try:
                tweetInsights = twitter.sentiment(twitterAPI, 7, search_phrase)
                newsInsights = newsapi(search_phrase)
                if len(tweetInsights) == 0 and len(newsInsights) == 0:
                    return render_template("insights.html", method="POST", search_phrase=search_phrase)
                elif len(tweetInsights) == 0:
                    return render_template("insights.html", method="POST", news=newsInsights, search_phrase=search_phrase)
                elif len(newsInsights) == 0:
                    return render_template("insights.html", method = "POST", tweets = tweetInsights, search_phrase=search_phrase)
                else:
                    return render_template("insights.html", method = "POST", tweets = tweetInsights, news=newsInsights)
            except Exception as inst:
                return apology(str(inst))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    userInfo = UserInfo()[0]
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol").upper()
        number = request.form.get("number")
        if not symbol or not number:
            return apology("Invalid input")
        number = int(number)
        quote = lookup(symbol)
        if quote != None:
            cost = float(number) * quote["price"]
            cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])[0]
            if cost > cash['cash']:
                return apology("You do not have enough cash")
            else:
                db.execute("UPDATE users SET cash = :remaining WHERE id = :id", remaining = cash['cash'] - cost, id = session["user_id"])
                stockExists = db.execute("SELECT number FROM :username WHERE symbol=:symbol", username=userInfo['username'], symbol=symbol)
                if len(stockExists) == 0:
                    db.execute("INSERT INTO :username ('symbol', 'number') VALUES (:symbol, :number)", username=userInfo['username'], symbol = symbol, number = float(number))
                else:
                    db.execute("UPDATE :username SET number = :number WHERE symbol = :symbol", username=userInfo['username'], number = (number + int(stockExists[0]['number'])), symbol = symbol)
                db.execute("INSERT INTO :tablename ('symbol','number', 'price', 'nature') VALUES (:symbol, :number, :price, 'b')", tablename=(userInfo['username'] + "History"), symbol=symbol, number=number, price=quote['price'])
        else:
            return apology(symbol + " is an invalid symbol")
        return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    userInfo = UserInfo()[0]
    if request.method == "GET":
        stock_list = db.execute("SELECT symbol FROM :username", username=userInfo['username'])
        if len(stock_list) < 1:
            return render_template("sell.html")
        else:
            return render_template("sell.html", stock_list=stock_list)
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

@app.route("/history")
@login_required
def history():
    userInfo = UserInfo()[0]
    history = db.execute("SELECT * FROM :tablename", tablename=(userInfo['username'] + "History"))
    if not history:
        return render_template("history.html")
    else:
        return render_template("history.html", history=history)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    userInfo = UserInfo()[0]
    dp = "static/dp/" + userInfo['username'] + "." + userInfo['dp']
    if not os.path.exists(dp):
        dp = "../static/dp/"+"default.png"
    else:
        dp = "../static/dp/" + userInfo['username'] + "." + userInfo['dp']
    if request.method == "GET":
        return render_template("profile.html", username=userInfo['username'], bio=userInfo['bio'], dp=dp)
    else:
        search_string = request.form.get("username")
        new_bio = request.form.get("bio")
        dp_file = request.form.get("dp_upload")
        #TODO Search Engine to find relevant matches
        if search_string:
            matches = db.execute("SELECT username, bio FROM users WHERE id!=:user_id", user_id=session["user_id"])
            results = []
            for match in matches:
                if match["username"] == search_string:
                    results.append(match)
            if not results:
                return render_template("profile.html", method="POST", username=userInfo['username'], bio=userInfo['bio'], dp=dp)
            else: 
                return render_template("profile.html", method="POST", results=results, username=userInfo['username'], bio=userInfo['bio'], dp=dp)
        elif new_bio:
            db.execute("UPDATE users SET bio=:new_bio WHERE id=:user_id", new_bio=new_bio, user_id=session["user_id"])
            return redirect("/profile")
        elif dp_file:
            filename = secure_filename(dp_file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            db.execute("UPDATE users SET dp=:new_dp WHERE id=:user_id", new_dp=file_extension, user_id=session["user_id"])
            dp_file.save('static/dp/' + userInfo['username'] + "." + file_extension)
            return redirect("/profile")
        else:
            return redirect("/profile")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
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
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
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
            db.execute("CREATE TABLE IF NOT EXISTS :tablename ('transaction' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'symbol' TEXT NOT NULL,'number' NUMERIC NOT NULL, 'price' NUMERIC NOT NULL, 'timestamp' DATETIME DEFAULT CURRENT_TIMESTAMP, 'nature' TEXT DEFAULT 'na')", tablename=tablename)
            return redirect("/")
        # Check for error
        except Exception as inst:
            if "unique constraint failed" in str(inst).lower():
                return apology("Username already taken")
            else:
                return apology(str(inst))

"""
@app.route("/chat", methods=["GET", "POST"])
#@login_required
def chat():
    return render_template("chat.html")

@socketio.on('connect', namespace='/chat')
def handle_connect(response):
    print("Response:", response)

@socketio.on('message', namespace='/chat')
def handle_message(sid, message):
    print("Socket:", sid, "Message:", message)
    send(message, namespace='/chat', broadcast=True)
"""

def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    socketio.run(app, debug=True)