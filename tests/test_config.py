from icw import app
import os


def test_config_read():
    assert app.config['ALLOWED_EXTENSIONS'] == set(['csv'])
    if os.getenv('TRAVIS'):
        assert app.config['SECRET_KEY'] == 'SUPER_SECRET_KEY'
    else:
        assert app.config['SECRET_KEY'] != 'SUPER_SECRET_KEY'
