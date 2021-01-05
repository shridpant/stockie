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
from cs50 import SQL
from werkzeug.utils import secure_filename
from flask import Blueprint, redirect, render_template, request
from src.helpers import apology, login_required, UserInfo

profile = Blueprint("profile", __name__, static_folder="static", template_folder="templates")
db = SQL("sqlite:///src/finance.db")

@profile.route("/", methods = ["GET", "POST"])
@profile.route("/me", methods=["GET", "POST"])
@login_required
def my_profile():
    userInfo = UserInfo()[0]
    dp = "static/dp/" + userInfo['username'] + "." + userInfo['dp']
    if not os.path.exists(dp):
        dp = "../../static/dp/"+"default.png"
    else:
        dp = "../../static/dp/" + userInfo['username'] + "." + userInfo['dp']
    if request.method == "GET":
        return render_template("profiles/my_profile.html", userInfo=userInfo, dp=dp)
    else:
        search_string = request.form.get("username")
        new_bio = request.form.get("bio")
        new_email = request.form.get("email")
        new_phone = request.form.get("phone")
        if request.form.get("dp_submit"):
            dp_file = request.files['dp_upload']
        else :
            dp_file=""
        #TODO Search Engine to find relevant matches
        if search_string:
            matches = db.execute("SELECT username, bio FROM users WHERE id!=:user_id", user_id=userInfo["id"])
            results = []
            for match in matches:
                if match["username"] == search_string:
                    results.append(match)
            if not results:
                return render_template("profiles/my_profile.html", method="POST", userInfo=userInfo, dp=dp)
            else: 
                return render_template("profiles/my_profile.html", method="POST", results=results, userInfo=userInfo, dp=dp)
        elif new_bio or new_email or new_phone:
            to_update = [["bio", new_bio], ["email", new_email], ["phone", new_phone]]
            for parameter in to_update:
                if parameter[1]:
                    db.execute("UPDATE users SET :param=:new_param WHERE id=:user_id", param=parameter[0], new_param=parameter[1], user_id=userInfo["id"])
            return redirect("/profile/")
        elif dp_file:
            filename = secure_filename(dp_file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            db.execute("UPDATE users SET dp=:new_dp WHERE id=:user_id", new_dp=file_extension, user_id=userInfo["id"])
            dp_file.save('static/dp/' + userInfo['username'] + "." + file_extension)
            return redirect("/profile/")
        else:
            return redirect("/profile/")

@profile.route("/user/<target_uname>", methods=['GET'])
@login_required
def target_profile(target_uname):
    userInfo = UserInfo()[0]
    if target_uname == userInfo['username']:
        return redirect("/profile/")
    match=db.execute("SELECT * FROM users WHERE username=:target_uname", target_uname=target_uname)
    if not match:
        return apology("User not found!", 404)
    dp = "static/dp/" + match[0]['username'] + "." + match[0]['dp']
    if not os.path.exists(dp):
        dp = "../../static/dp/"+"default.png"
    else:
        dp = "../../static/dp/" + match[0]['username'] + "." + match[0]['dp']
    return render_template("profiles/target_profile.html", dp=dp, user=match[0])
