import pytest
import os
import sys

sys.path.insert(0, os.getcwd())
import gae_pathfix  # noqa
from icw import app  # noqa

app.testing = True
app.config['WTF_CSRF_ENABLED'] = False
app.debug = True


@pytest.fixture(scope="session")
def client():
    with app.test_client() as client:
        yield client
