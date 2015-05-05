from icw import app


def test_config_read():
    assert app.config['ALLOWED_EXTENSIONS'] == set(['csv'])
