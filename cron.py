from google.appengine.ext.webapp.util import run_wsgi_app
from flask import Flask
import cloudstorage as gcs
import time

app = Flask(__name__)


app.config.from_object('config')

my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)


@app.route('/cron/clean_bucket')
def clean_bucket():
    bucket_name = app.config['BUCKET_NAME']

    for each in gcs.listbucket('/' + bucket_name):
        age = time.time() - each.st_ctime
        # Delete files over an hour old
        if age > 3600:
            gcs.delete(each.filename, retry_params=my_default_retry_params)

    # 204 response: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    return ('', 204)

run_wsgi_app(app)
