import pytest
import os
import sys

sys.path.insert(0, os.getcwd())

import gae_pathfix  # noqa
from icw import app

app.testing = True
app.config['WTF_CSRF_ENABLED'] = False


@pytest.yield_fixture
def client():
    with app.test_client() as client:
        yield client
