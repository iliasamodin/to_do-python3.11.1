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
from flask import abort                                    # Importing function that raises http exception by error code
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
def close_db_connection(response):
    if hasattr(g, "connection_to_db"):
        g.connection_to_db.close()                          # Closing the database connection after processing a request
    return response


page_title = "To-Do"


@app.route("/")        # The decorator responsible for linking the path in the url with the view that works on this link
def welcome_to_to_do():
    if current_user.is_authenticated:
        return redirect(url_for("current_tasks_to_do"))

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
            if g.connection_to_db.get_first_record("users", username=username) is None:
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
        except sqlite3.OperationalError:
            flash("Invalid value entered")

    return render_template("to_do/sign_up_to_do.html", page_title=page_title)


@app.route("/login/", methods=["GET", "POST"])
def login_to_do():
    if request.method == "POST":
        try:
            username = request.form["username"]
            user = g.connection_to_db.get_first_record("users", username=username)
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
        except sqlite3.OperationalError:
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
        except sqlite3.OperationalError:
            flash("Invalid value entered")

    return render_template("to_do/create_task_to_do.html", page_title=page_title, today=today, now=now)


@app.route("/tasks-for-today/", methods=["GET", "POST"])
@login_required
def tasks_for_today_to_do():
    page_name = "tasks-for-today"
    main_title = "Tasks for today"

    today, now = datetime.now().strftime("%Y-%m-%d&%H:%M").split("&")
    user_id = current_user.get_id()
    tasks = g.connection_to_db.get_tasks_for_user(
        user_id, 
        filters=f"date_of_completion = {repr(today)}",
        order_by=f"execution_status, time_of_completion, priority DESC, title"
    )

    if request.method == "POST":
        try:
            task_id = int(request.form["task_id"])
            execution_status = int(request.form["execution_status"])
            g.connection_to_db.update_task(
                task_id, 
                execution_status=execution_status, 
                date_of_completion=today,
                time_of_completion=now
            )
        finally:
            return redirect(url_for("tasks_for_today_to_do"))

    return render_template("to_do/tasks_to_do.html", 
        page_title=page_title, 
        page_name=page_name,
        main_title=main_title,
        tasks=tasks
    )


@app.route("/current-tasks/", methods=["GET", "POST"])
@login_required
def current_tasks_to_do():
    page_name = "current-tasks"
    main_title = "Current tasks"

    user_id = current_user.get_id()
    tasks = g.connection_to_db.get_tasks_for_user(
        user_id, 
        filters=f"execution_status = False",
        order_by=f"date_of_completion, time_of_completion, priority DESC, title"
    )

    if request.method == "POST":
        today, now = datetime.now().strftime("%Y-%m-%d&%H:%M").split("&")

        try:
            task_id = int(request.form["task_id"])
            execution_status = int(request.form["execution_status"])
            g.connection_to_db.update_task(
                task_id, 
                execution_status=execution_status, 
                date_of_completion=today,
                time_of_completion=now
            )
        finally:
            return redirect(url_for("current_tasks_to_do"))

    return render_template("to_do/tasks_to_do.html", 
        page_title=page_title,
        page_name=page_name,
        main_title=main_title,
        tasks=tasks
    )


@app.route("/completed-tasks/", methods=["GET", "POST"])
@login_required
def completed_tasks_to_do():
    page_name = "completed-tasks"
    main_title = "Completed tasks"

    user_id = current_user.get_id()
    tasks = g.connection_to_db.get_tasks_for_user(
        user_id, 
        filters=f"execution_status = True",
        order_by=f"date_of_completion DESC, time_of_completion DESC, priority DESC, title"
    )

    if request.method == "POST":
        today, now = datetime.now().strftime("%Y-%m-%d&%H:%M").split("&")

        try:
            task_id = int(request.form["task_id"])
            execution_status = int(request.form["execution_status"])
            g.connection_to_db.update_task(
                task_id, 
                execution_status=execution_status, 
                date_of_completion=today,
                time_of_completion=now
            )
        finally:
            return redirect(url_for("completed_tasks_to_do"))

    return render_template("to_do/tasks_to_do.html", 
        page_title=page_title,
        page_name=page_name,
        main_title=main_title,
        tasks=tasks
    )


@app.route("/<calling_page>/task-<int:task_id>/", methods=["GET", "POST"])
@login_required
def change_task_to_do(calling_page, task_id):
    user_id = current_user.get_id()
    task = g.connection_to_db.get_first_record("tasks", id=task_id, user_id=user_id)
    if task is None:
        abort(404)

    if request.method == "POST":
        try:
            form_data = dict(request.form)
            form_data["execution_status"] = 1 if form_data.get("execution_status") else 0
            g.connection_to_db.update_task(task_id, **form_data)

            return redirect(url_for(f"{calling_page.replace('-', '_')}_to_do"))
        except sqlite3.OperationalError:
            flash("Invalid value entered")

    return render_template("to_do/change_task_to_do.html", 
        page_title=page_title,
        page_name=calling_page,
        task=task
    )


@app.route("/<calling_page>/task-<int:task_id>/deleting/", methods=["GET", "POST"])
@login_required
def deleting_task(calling_page, task_id):
    if request.method == "POST":
        try:
            user_id = current_user.get_id()
            g.connection_to_db.delete_task(task_id, user_id)
        finally:
            return redirect(url_for(f"{calling_page.replace('-', '_')}_to_do"))


@app.errorhandler(404)
def page_not_found(exception):
    page_title = "Error"
    error = 404

    return render_template("error_page.html", page_title=page_title, error=error), error


@app.errorhandler(500)
def server_error(exception):
    page_title = "Error"
    error = 500

    return render_template("error_page.html", page_title=page_title, error=error), error


@app.errorhandler(403)
def permission_denied(exception):
    page_title = "Error"
    error = 403

    return render_template("error_page.html", page_title=page_title, error=error), error


@app.errorhandler(400)
def bad_request(exception):
    page_title = "Error"
    error = 400

    return render_template("error_page.html", page_title=page_title, error=error), error


if __name__ == "__main__":
    app.run(port=8000, debug=True)