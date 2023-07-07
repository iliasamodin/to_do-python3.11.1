# Importing a Flask class that generates a central framework object that implements a WSGI application
from flask import Flask
import os

# Application Configuration
SECRET_KEY = "wxkF'admzE0j}K>@q:Q`8`5#UPeL-Rl-,NYm:J*DaVyhNY[A+3y_I<,4"
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, "/db.sqlite3")))

if __name__ == "__main__":
    app.run(debug=True)