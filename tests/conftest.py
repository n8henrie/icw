"""Provide pytest setup for icw."""

import pytest

from icw import app

app.testing = True
app.config["WTF_CSRF_ENABLED"] = False
app.debug = True


@pytest.fixture(scope="session")
def client():
    """Provide client testing fixture."""
    with app.test_client() as test_client:
        yield test_client
