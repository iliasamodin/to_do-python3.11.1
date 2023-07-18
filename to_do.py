# Importing a Flask class that generates a central framework object that implements a WSGI application
from flask import Flask
from flask import render_template                   # Import html template render function into dynamic page with jinja2
# Importing functions to redirect requests to other views and to generate a url from the name of a view
from flask import redirect, url_for
# Import object containing information about the context of the request,
#   the flash function for passing quick messages to template
#   and the g object intended for passing the values of variables 
#   from one view to another within a single request to the site
from flask import request, flash, g
# Importing a class for working with user authorization 
#   and functions for performing authorization from the external library flask_login
from flask_login import LoginManager, login_user
# Importing a decorator that restricts unauthorized users from accessing views that are wrapped with this decorator
from flask_login import login_required
from flask_login import logout_user                        # Importing the function to log out the user from the account
# Importing a variable referring to an object of the UserLogin class corresponding to the user index 
#   from the session of the current http request
from flask_login import current_user
# Import a function that hashes the user's password to store the hash sum of the password in the database
from werkzeug.security import generate_password_hash
# Importing a function to match the hash sum of the user's password from the database 
#   with the user's password received through the authorization form
from werkzeug.security import check_password_hash
# Importing class for executing sql queries to the database and user authorization class
from superstructures import ConnectionToDB, UserLogin
from datetime import datetime
import sqlite3, os

# Application Configuration
SECRET_KEY = "wxkF'admzE0j}K>@q:Q`8`5#UPeL-Rl-,NYm:J*DaVyhNY[A+3y_I<,4"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "db.sqlite3")))
login_manager = LoginManager(app)              # Declaring an authorization class object based on the application-object
# Declaring a view that processes requests from unauthorized users 
#   to pages that require authorization in the request session
login_manager.login_view = "login_to_do"


def db_connection():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row                           # Converting records from tables to a dictionary type
    return connection


# Decorator that characterizes a function inside the application as code 
#   that must be executed after the http request is accepted by the web server, 
#   but before the corresponding view is processed
@app.before_request
def connection_to_db_via_g():  # Implementing a single database connection across the entire query
    # Checking whether a connection was previously made in the database within the current request
    if not hasattr(g, "connection_to_db"):
        g.connection_to_db = ConnectionToDB(db_connection())


# A decorator that wraps a function that forms an object of the authorization class 
#   based on the user_id recorded in the session of the current request
# The function wrapped with the user_loader decorator is executed only 
#   if the user_id is present in the session of the current request. 
#   In this case, the wrapped function will be executed before the before_request decorator function
@login_manager.user_loader
def user_loading(user_id):
    connection_to_db_via_g()
    return UserLogin(user_id, g.connection_to_db)


@app.teardown_appcontext                         # Decorator responsible for processes executed after request processing
def close_db_connection(error):
    if hasattr(g, "connection_to_db"):
        g.connection_to_db.close()                                   # Closing the database connection after processing a request


page_title = "To-Do"


@app.route("/")        # The decorator responsible for linking the path in the url with the view that works on this link
def welcome_to_to_do():
    return render_template("to_do/welcome_to_to_do.html", page_title=page_title)


# The "methods" argument to the "route" method on the application object takes a list of methods 
#   that the page view can process. 
#   By default, the "methods" argument is equals to a list with one "get" method. 
#   The "get" method must be passed to the "methods" argument, since the "get" method is used to request "html" pages
@app.route("/sign-up/", methods=["GET", "POST"])
def sign_up_to_do():
    if request.method == "POST":
        try:
            username = request.form["username"]
            if g.connection_to_db.get_first_record("users", "username", username) is False:
                password = request.form["password1"]
                if password == request.form["password2"]:
                    hash_sum_of_password = generate_password_hash(password)
                    new_user = g.connection_to_db.add_new_user(username, hash_sum_of_password)
                    # Authorization with remembering the registered user
                    login_user(UserLogin(user=new_user), remember=True)

                    return redirect(url_for("current_tasks_to_do"))
                else: 
                    # Instant messages allow you to add information to the html template 
                    #   in response to user actions on the page
                    flash("Different passwords entered")
            else:
                flash("User with the same name already exists")
        except ValueError:
            flash("Invalid value entered")

    return render_template("to_do/sign_up_to_do.html", page_title=page_title)


@app.route("/login/", methods=["GET", "POST"])
def login_to_do():
    if request.method == "POST":
        try:
            username = request.form["username"]
            user = g.connection_to_db.get_first_record("users", "username", username)
            if user and check_password_hash(user["password"], request.form["password"]):
                login_user(UserLogin(user=user), remember=True)

                # If the next method is present in the get-request of the authorization page, 
                #   then the authorization page was requested by redirecting an unauthorized user 
                #   using the login_required decorator, 
                #   so after authorization the user is redirected to the page 
                #   that was requested before login_required was triggered
                return redirect(request.args.get("next") or url_for("current_tasks_to_do"))
            else:
                flash("There is no user with this username and password")
        except ValueError:
            flash("Invalid value entered")

    return render_template("to_do/login_to_do.html", page_title=page_title)


@app.route("/logout/", methods=["GET", "POST"])
@login_required
def logout_to_do():
    if request.method == "POST":
        logout_user()
        return redirect(url_for("welcome_to_to_do"))


@app.route("/<calling_page>/create-task/", methods=["GET", "POST"])
@login_required
def create_task_to_do(calling_page):
    today, now = datetime.now().strftime("%Y-%m-%d&%H:%M").split("&")

    if request.method == "POST":
        try:
            user_id = current_user.get_id()
            g.connection_to_db.add_new_task(user_id, request.form)

            return redirect(url_for(f"{calling_page.replace('-', '_')}_to_do"))
        except ValueError:
            flash("Invalid value entered")

    return render_template("to_do/create_task_to_do.html", page_title=page_title, today=today, now=now)


@app.route("/tasks-for-today/")
@login_required
def tasks_for_today_to_do():
    return "pass"


@app.route("/current-tasks/")
@login_required
def current_tasks_to_do():
    return "pass"


@app.route("/completed-tasks/")
@login_required
def completed_tasks_to_do():
    return "pass"


@app.route("/<calling_page>/task-<int:task_id>/")
@login_required
def change_task_to_do(calling_page, task_id):
    return "pass"


if __name__ == "__main__":
    app.run(port=8000, debug=True)