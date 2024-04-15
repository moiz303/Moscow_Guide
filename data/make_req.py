from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class Reqest(FlaskForm):
    req = StringField('Введите интересующее место', validators=[DataRequired()])
    submit = SubmitField('Узнать больше')
