"""config.py
Contains the default config class for icw.
"""


class DefaultConfig(object):
    DEBUG = False
    ALLOWED_EXTENSIONS = set(['csv'])
    SECRET_KEY = 'SUPER_SECRET_KEY'
    BUCKET_NAME = 'my_bucket'
