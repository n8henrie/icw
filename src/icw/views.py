"""Flask views for icw."""
import typing as t
import uuid
from pathlib import Path

from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.wrappers import Response

from . import __version__ as icw_version
from . import app
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
LINKS_TITLE = "A few helpful links"


@app.route("/", methods=["GET", "POST"])
def index() -> Response:
    """Provide default route."""
    form = UploadForm()
    if request.method == "POST" and form.validate_on_submit():
        key = str(uuid.uuid4())
        fullpath = Path(f"/tmp/{key}.ics")

        upfile = request.files["csv_file"]

        try:
            ics_file = convert(upfile)

        except (ContentError, HeadersError, DatetimeFormatError) as error:
            app.logger.info("Error in file conversion: ")
            app.logger.info(error)
            flash(str(error), "danger")
            return render_template(
                "index.html",
                form=form,
                links=base_links,
                links_title=LINKS_TITLE,
                version=icw_version,
            )

        else:
            app.logger.info("File converted without errors")
            fullpath.write_bytes(ics_file)

            session["key"] = key
            return redirect(url_for("success"))

    for _, errors in form.errors.items():
        for err in errors:
            msg = f"Whups! {err}"
            flash(msg)
    return render_template(
        "index.html",
        form=form,
        links=base_links,
        links_title=LINKS_TITLE,
        version=icw_version,
    )


@app.route("/success")
def success() -> Response:
    """Provide route for successful conversion."""
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
        "success.html",
        links=links,
        links_title="Where to next?",
        version=icw_version,
    )


@app.route("/download")
def download() -> Response:
    """Provide route for downloading converted file."""
    key = session["key"]
    fullpath = "/tmp/" + key + ".ics"
    mtype = "text/calendar"
    with open(fullpath, "rb") as f:
        downfile = f.read()

    response = make_response(downfile)
    response.headers["Content-Type"] = mtype
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=converted.ics"
    return response


@app.errorhandler(404)
def error_404(_: t.Any) -> Response:
    """Return a custom 404 error."""
    return make_response("Sorry, Nothing at this URL.", 404)


@app.errorhandler(500)
def error_500(e) -> Response:
    """Return a custom 500 error."""
    app.logger.exception(e)
    app.logger.warning(repr(e))
    app.logger.warning(e)
    msg = (
        f"Sorry, unexpected error: {e}<br/><br/>"
        "This shouldn't have happened. Would you mind "
        '<a href="https://n8henrie.com/contact">sending me</a> '
        "a message regarding what caused this (and the file if possible)? "
        "Thanks -Nate"
    )
    return make_response(msg, 500)
