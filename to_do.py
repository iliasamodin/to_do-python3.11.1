# Importing a Flask class that generates a central framework object that implements a WSGI application
from flask import Flask
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


if __name__ == "__main__":
    app.run(debug=True)