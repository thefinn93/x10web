#!/usr/bin/env python3
from flask import Flask, request, session, abort, render_template
import random
import string
import json
import sys
from sh import heyu
app = Flask(__name__, static_url_path="")

HOUSECODES = string.ascii_uppercase
MAXUNIT = 16
ACTIONS = ['on', 'off', 'bright', 'bright', 'dim', 'dimb']
chars = string.ascii_uppercase + string.digits

app.secret_key = ''.join(random.SystemRandom().choice(chars) for _ in range(30))


try:
    config = json.load(open('x10web.conf'))
except IOError:
    sys.stderr.write("Looks like x10web.conf doesn't exit! Check out x10web.example.conf for ideas")
    sys.exit(1)

app.jinja_env.globals['units'] = config['units']


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/token")
def getToken():
    return generate_csrf_token()


@app.route("/api/action", methods=["POST"])
def takeAction():
    if "housecode" not in request.form:
        raise Exception("No housecode specified!")
    housecode = request.form["housecode"].upper()
    if housecode not in HOUSECODES:
        raise Exception("Invalid house code!")

    if "action" not in request.form:
        raise Exception("No action specified!")
    action = request.form["action"].lower()
    if action not in ACTIONS:
        raise Exception("Invalid action!")

    if "unit" not in request.form:
        raise Exception("No unit specified!")
    unit = int(request.form["unit"])
    if unit < 0 or unit > MAXUNIT:
        raise Exception("Invalid unit!")

    heyu(action, "%s%0.d" % (housecode, unit))
    return "ok"


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get('_csrf_token')
        if not token or token != request.form.get('token'):
            abort(403)


@app.errorhandler(403)
def unauthorized(e):
    return session.get('_csrf_token')


def generate_csrf_token():
    if '_csrf_token' not in session:
        app.logger.debug("Creating a CSRF token...")
        session['_csrf_token'] = ''.join(random.SystemRandom().choice(chars) for _ in range(30))
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token


if __name__ == "__main__":
    debug = "debug" in config and config['debug']
    host = "127.0.0.1"
    if "host" in config:
        host = config['host']
    app.run(debug=debug, host=host)
