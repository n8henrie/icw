"""Tests related to configuration."""
from icw import app


def test_config_read():
    """Test reading the default config."""
    assert app.config["ALLOWED_EXTENSIONS"] == set(["csv"])
