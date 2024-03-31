from flask import *
from threading import Thread

import userhandling

# TODO comment code

Thread(target=userhandling.expiredSessionHandlerThread).start()

app = Flask(__name__)

@app.route("/")
def index():
    session_id = request.cookies.get("session_id")
    user_id = request.cookies.get("user_id")
    userhandling.readSession(session_id, user_id)  # TODO actually use this

    return render_template("index.html", pfp="/static/favicon.png") # returns homepage with user's pfp

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html") # returns registration form

    elif request.method == "POST":
        rejected = userhandling.userSignUp(request.form)
        if rejected:
            return render_template("register.html", rejectreasons=rejected) # jinja will deal with rendering rejection
        else:
            session_id = userhandling.makeSession(request.form["username"])
            resp = make_response(redirect("/profile"))
            resp.set_cookie("session_id", session_id)
            resp.set_cookie("user_id", request.form["username"].lower()) # TODO session id instead of username
            return resp

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session_id = request.cookies.get("session_id") # check if logged in TODO check if session has expired
        user_id = request.cookies.get("user_id")
        
        if userhandling.readSession(session_id, user_id):
            return redirect("/profile")
        else:
            return render_template("login.html") # TODO reset password option (email link)
        
    elif request.method =="POST":
        rejected = userhandling.userLogin(request.form)
        
        if rejected:
            return render_template("login.html", rejectreasons=rejected)
        else:
            session_id = userhandling.makeSession(request.form["username"])
            resp = make_response(redirect("/profile"))
            resp.set_cookie("session_id", session_id)
            resp.set_cookie("user_id", request.form["username"].lower())
            return resp

@app.route("/profile")
def profile():
    session_id = request.cookies.get("session_id")
    user_id = request.cookies.get("user_id")

    if session_id:
        if userhandling.readSession(session_id, user_id):
            return render_template("profile.html", username=user_id) # TODO make an actual profile page
    else:
        return redirect("/login")
    # TODO option to upload pfp (validate upload data)
    # TODO option to change email
    # TODO option to delete account
    # TODO option to change password

@app.route("/logout", methods=["GET", "POST"])
def logout():
    resp = make_response(render_template("logout.html"))
    if request.method == "POST":
        if request.form["logout"] == "logout":
            resp.set_cookie("session_id", "")
            resp.set_cookie("user_id", "") #set session_id cookie to blank

    return resp

@app.route("/about")
def about():
    return render_template("about.html") # static page

@app.route("/contact")
def contact():
    return render_template("contact.html") # static page

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password-start.html") # TODO add a forgot password form

app.run()