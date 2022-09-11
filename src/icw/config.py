"""Config classes for icw."""


class DefaultConfig(object):
    """Contains the default config class for icw."""

    DEBUG = False
    ALLOWED_EXTENSIONS = set(["csv"])
    SECRET_KEY = "SUPER_SECRET_KEY"
    GOOGLE_ANALYTICS_ID = "GOOGLE_ANALYTICS_ID"
    GOOGLE_ANALYTICS_DOMAIN = "GOOGLE_ANALYTICS_DOMAIN"
