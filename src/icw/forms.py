"""Forms for icw."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField


class UploadForm(FlaskForm):
    """Form that accepts the CSV input file."""

    validators = [
        FileRequired(message="There was no file!"),
        FileAllowed(["csv"], message="Must be a csv file!"),
    ]

    csv_file = FileField("", validators=validators)
    submit = SubmitField(label="Convert")
