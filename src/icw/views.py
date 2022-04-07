import uuid

from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from icw import app

from .converter import ContentError, convert, DatetimeFormatError, HeadersError
from .forms import UploadForm

base_links = [
    {
        "url": "http://n8henrie.com/2013/05/spreadsheet-to-calendar/",
        "description": "Instructional post",
    },
    {
        "url": "https://github.com/n8henrie/icw",
        "description": "icw source code at GitHub",
    },
]
links_title = "A few helpful links"


@app.route("/", methods=["GET", "POST"])
def index():

    form = UploadForm()
    if request.method == "POST" and form.validate_on_submit():
        key = str(uuid.uuid4())
        filename = key + ".ics"
        fullpath = "/" + filename

        upfile = request.files["csv_file"]

        try:
            ics_file = convert(upfile)

        except (ContentError, HeadersError, DatetimeFormatError) as error:
            app.logger.info("Error in file conversion: ")
            app.logger.info(error)
            flash(error, "danger")
            return render_template(
                "index.html",
                form=form,
                links=base_links,
                links_title=links_title,
            )

        else:
            app.logger.info("File converted without errors")
            with open("/tmp/" + fullpath, "w") as w:
                w.write(ics_file.decode())

            session["key"] = key
            return redirect(url_for("success"))

    for field, errors in form.errors.items():
        for error in errors:
            msg = "Whups! {}".format(error)
            flash(msg)
    return render_template(
        "index.html", form=form, links=base_links, links_title=links_title
    )


@app.route("/success")
def success():
    links = [
        {"url": "/", "description": "Convert another file"},
        {
            "url": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick"
            "&hosted_button_id=ZCCTV6VCCS8J2",
            "description": "Buy me a coffee",
        },
    ]
    links.extend(base_links)

    return render_template(
        "success.html", links=links, links_title="Where to next?"
    )


@app.route("/download")
def download():
    key = session["key"]
    fullpath = "/tmp/" + key + ".ics"
    mtype = "text/calendar"
    with open(fullpath) as r:
        downfile = r.read()

    response = make_response(downfile)
    response.headers["Content-Type"] = mtype
    response.headers["Content-Disposition"] = (
        "attachment; " "filename=converted.ics"
    )
    return response


@app.errorhandler(404)
def error_404(e):
    """Return a custom 404 error."""
    return "Sorry, Nothing at this URL.", 404


@app.errorhandler(500)
def error_500(e):
    """Return a custom 500 error."""
    msg = (
        "Sorry, unexpected error: {}<br/><br/>"
        "This shouldn't have happened. Would you mind "
        '<a href="https://n8henrie.com/contact">sending me</a> '
        "a message regarding what caused this (and the file if "
        "possible)? Thanks -Nate".format(e)
    )
    return msg, 500
