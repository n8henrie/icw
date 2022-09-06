import pytest

from icw import app  # noqa

app.testing = True
app.config["WTF_CSRF_ENABLED"] = False
app.debug = True


@pytest.fixture(scope="session")
def client():
    with app.test_client() as client:
        yield client
