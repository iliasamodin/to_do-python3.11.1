# Importing a Flask class that generates a central framework object that implements a WSGI application
from flask import Flask
from flask import render_template                   # Import html template render function into dynamic page with jinja2
import sqlite3, os

# Application Configuration
SECRET_KEY = "wxkF'admzE0j}K>@q:Q`8`5#UPeL-Rl-,NYm:J*DaVyhNY[A+3y_I<,4"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "db.sqlite3")))


def db_connection():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row                           # Converting records from tables to a dictionary type
    return connection


page_title = "To-Do"


@app.route("/")        # The decorator responsible for linking the path in the url with the view that works on this link
def welcome_to_to_do():
    return render_template("to_do/welcome_to_to_do.html", page_title=page_title)


@app.route("/sign-up/")
def sign_up_to_do():
    return "pass"


@app.route("/login/")
def login_to_do():
    return "pass"


@app.route("/<calling_page>/create-task/")
def create_task_to_do(calling_page):
    return "pass"


@app.route("/tasks-for-today/")
def tasks_for_today_to_do():
    return "pass"


@app.route("/current-tasks/")
def current_tasks_to_do():
    return "pass"


@app.route("/completed-tasks/")
def completed_tasks_to_do():
    return "pass"


@app.route("/<calling_page>/task-<int:task_id>/")
def change_task_to_do(calling_page, task_id):
    return "pass"


if __name__ == "__main__":
    app.run(port=8000, debug=True)