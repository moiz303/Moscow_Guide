from flask_wtf import FlaskForm
from wtforms import SubmitField


class TTS(FlaskForm):
    submit = SubmitField('Озвучить текст')
