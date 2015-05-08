from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


class UploadForm(Form):

    validators = [
        FileRequired(message='There was no file!'),
        FileAllowed(['csv'], message='Must be a csv file!')
    ]

    csv_file = FileField('', validators=validators)
    submit = SubmitField(label="Convert")
