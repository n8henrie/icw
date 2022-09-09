"""Top level of icw.py"""

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect

__version__ = "2.0.0"

app = Flask(__name__)

# Default config from class inside inside config
app.config.from_object("icw.config.DefaultConfig")

# Production config from file (not in VCS)
app.config.from_envvar("ICW_CONFIG", silent=True)

Bootstrap(app)
CSRFProtect(app)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
import icw.views  # noqa
