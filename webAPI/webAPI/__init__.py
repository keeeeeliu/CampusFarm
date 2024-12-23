"""webAPI package initializer."""
import flask
from flask_cors import CORS

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name
CORS(app)  # Enable CORS for all routes

# Read settings from config module (webAPI/config.py)
app.config.from_object('webAPI.config')

# Overlay settings read from a Python file whose path is set in the environment
# variable WEBAPI_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export WEBAPI_SETTINGS=secret_key_config.py
app.config.from_envvar('WEBAPI_SETTINGS', silent=True)

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import webAPI.api  # noqa: E402  pylint: disable=wrong-import-position
import webAPI.model  # noqa: E402  pylint: disable=wrong-import-position

