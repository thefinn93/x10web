#!/usr/bin/env python3
from flask import Flask
import string
from sh import heyu
app = Flask(__name__, static_url_path="")

HOUSECODES = string.ascii_uppercase
MAXUNIT = 16
ACTIONS = ['on', 'off', 'bright', 'bright', 'dim', 'dimb']


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route("/api/<housecode>/<int:unit>/<action>")
def on(housecode, unit, action):
    housecode = housecode.upper()
    action = action.lower()
    if housecode not in HOUSECODES:
        raise Exception("Invalid house code!")
    if unit < 0 or unit > MAXUNIT:
        raise Exception("Invalid unit!")
    if action not in ACTIONS:
        raise Exception("Invalid action!")
    heyu(action, "%s%0.d" % (housecode, unit))
    return "ok"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
