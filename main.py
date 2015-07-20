#!/usr/bin/env python3
from flask import Flask, request, session, abort, render_template, Response
from functools import wraps
import random
import string
import json
import sys
from sh import heyu, git
app = Flask(__name__, static_url_path="")

HOUSECODES = string.ascii_uppercase
MAXUNIT = 16
ACTIONS = ['on', 'off']
chars = string.ascii_letters + string.digits


try:
    config = json.load(open('x10web.conf'))
except IOError:
    sys.stderr.write("Looks like x10web.conf doesn't exit! Check out x10web.example.conf for ideas")
    sys.exit(1)

if "secret" in config:
    app.secret = config["secret"]
    app.logger.debug("Using secret from config")
else:
    config["secret"] = ''.join(random.SystemRandom().choice(chars) for _ in range(30))
    app.secret_key = config["secret"]
    app.logger.debug("Generating new secret and attempting to save in config...")
    try:
        with open('x10web.conf', "w") as saveconfig:
            json.dump(config, saveconfig, indent=4, separators=(',', ': '))
    except IOError:
        app.logger.warning("Failed to save config file.")

app.jinja_env.globals['units'] = config['units']


def check_auth(username, password):
    if "auth" in config:
        if username in config['auth']:
            return config['auth'][username] == password
        else:
            return False
    else:
        return True


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if "auth"in config:
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
            else:
                return f(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated


def check_csrf(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "POST":
            token = session.get('_csrf_token')
            if not token or token != request.form.get('token'):
                abort(403)
            else:
                return f(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated


@app.route("/")
@requires_auth
def index():
    return render_template('index.html')


@app.route("/api/token")
@requires_auth
def getToken():
    return generate_csrf_token()


@app.route("/update", methods=["GET", "POST"])
def update():
    git("pull")
    return "kthx"


@app.route("/api/action", methods=["POST"])
@requires_auth
@check_csrf
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
