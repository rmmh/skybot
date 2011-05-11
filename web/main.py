#!/usr/bin/python

import sqlite3

db = sqlite3.connect

from flask import Flask

app = Flask("skybot")

@app.route("/")
def index():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)
