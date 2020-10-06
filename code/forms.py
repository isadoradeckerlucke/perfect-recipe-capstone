from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

# need: search form (but this could be better suited to being made in HTML?)
# want: user edit form

class LoginForm(FlaskForm):
    """form for logging in existing users"""
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [Length(min = 8)])

class AddUserForm(FlaskForm):
    """form for adding a new user"""

    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [Length(min = 8)])
    email = StringField('email', validators = [DataRequired(), Email()])
