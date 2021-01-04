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
from flask import Blueprint, redirect, render_template, request
from werkzeug.security import generate_password_hash
from src.helpers import apology

register = Blueprint("register", __name__, static_folder="static", template_folder="templates")

@register.route("/", methods=["GET", "POST"])
def landing():
    db = SQL("sqlite:///src/finance.db")
    if request.method == "GET":
        return render_template("auth/register.html")
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
            tablename = username + "History"
            table_existence = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=:tablename;", tablename=tablename)
            if not table_existence:
                db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=generate_password_hash(password))
                db.execute("CREATE TABLE IF NOT EXISTS :username ('symbol' TEXT NOT NULL PRIMARY KEY, 'number' NUMERIC NOT NULL)", username=username)
                db.execute("CREATE TABLE IF NOT EXISTS :tablename ('transaction' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'symbol' TEXT NOT NULL,'number' NUMERIC NOT NULL, 'price' NUMERIC NOT NULL, 'timestamp' DATETIME DEFAULT CURRENT_TIMESTAMP, 'nature' TEXT DEFAULT 'na')", tablename=tablename)
                return redirect("/")
            else:
                return apology("Username already taken")
        # Check for error
        except Exception as inst:
            return apology(str(inst))