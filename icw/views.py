from icw import app
from forms import UploadForm
from flask import (flash, make_response, redirect, render_template, request,
                   url_for, session)
import cloudstorage as gcs
import uuid
import converter
from converter import HeadersError, DatetimeFormatError, ContentError

base_links = [
    {'url': 'http://n8henrie.com/2013/05/spreadsheet-to-calendar/',
     'description': "Instructional post"},
    {'url': 'https://github.com/n8henrie/icw',
     'description': "icw source code at GitHub"}
    ]
links_title = "A few helpful links"


@app.route('/', methods=['GET', 'POST'])
def index():

    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():

        bucket_name = app.config['BUCKET_NAME']
        key = uuid.uuid4()
        filename = str(key) + '.ics'
        fullpath = '/' + bucket_name + '/' + filename

        upfile = request.files['csv_file']

        try:
            ics_file = converter.convert(upfile)

        except (ContentError, HeadersError, DatetimeFormatError) as error:
            flash(error)
            return render_template('index.html', form=form, links=base_links,
                                   links_title=links_title)

        else:
            mtype = 'text/calendar'
            with gcs.open(fullpath, 'w', content_type=mtype) as w:
                w.write(ics_file)

            session['key'] = key
            return redirect(url_for('success'))

    for field, errors in form.errors.items():
        for error in errors:
            msg = "Whups! {}".format(error)
            flash(msg)
    return render_template('index.html', form=form, links=base_links,
                           links_title=links_title)


@app.route('/success')
def success():
    links = [{'url': 'http://icw.n8henrie.com',
              'description': "Convert another file"},
             {'url': 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick'
              '&hosted_button_id=ZCCTV6VCCS8J2',
              'description': "Buy me a coffee"}]
    links.append(base_links)

    return render_template('success.html', links=links,
                           links_title="Where to next?")


@app.route("/download")
def download():
    bucket_name = app.config['BUCKET_NAME']
    key = session['key']
    fullpath = '/' + bucket_name + '/' + str(key) + '.ics'
    mtype = 'text/calendar'
    with gcs.open(fullpath) as r:
        downfile = r.read()
        # return send_file(r.name, mimetype=mtype, as_attachment=True,
        #     attachment_filename="converted.ics")

    # buf = io.BytesIO()
    # buf.write(downfile)
    # buf.seek(0)
    # return send_file(buf, mimetype=mtype, as_attachment=True,
    #     attachment_filename="converted.ics")

    response = make_response(downfile)
    response.headers['Content-Type'] = mtype
    response.headers["Content-Disposition"] = ("attachment; "
                                               "filename=converted.ics")
    return response


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)  # noqa
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
