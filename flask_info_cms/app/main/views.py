#!/Users/jasonlu/.virtualenvs/pyven3_6/bin/python
# Author: Jason Lu

from flask import Flask


app = Flask(__name__)

@app.route('/')
def index():
    return
