"""Top level of icw.py"""

# Import the Flask Framework
from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)

# Default config from class inside inside config
app.config.from_object('icw.config.DefaultConfig')

# Production config from file (not in VCS)
app.config.from_pyfile('../prod_config.py', silent=True)

Bootstrap(app)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
import icw.views  # noqa
