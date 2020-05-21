from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (InputRequired, DataRequired, NumberRange, Length, Email, 
                                EqualTo, ValidationError)

import re
import sys

from .models import User


class SearchForm(FlaskForm):
    search_query = StringField('Query', validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField('Search')


class CatReviewForm(FlaskForm):
    text = TextAreaField('Comment', validators=[InputRequired(), Length(min=5, max=500)])
    submit = SubmitField('Enter Comment')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=1, max=40)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            #user.delete()
            raise ValidationError('Username is taken')

    def validate_email(self, email):        
        user = User.objects(email=email.data).first()
        if user is not None:
            #user.delete()
            raise ValidationError('Email is taken')

    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('Password much be at least 8 characters long')
        string_check = re.compile(r'[@_!#$%^&*()<>?/\|}{~:]') 
        if string_check.search(password.data) == None:
            raise ValidationError('Password must contain a special character')
        if not (any(ch.isupper for ch in password.data)):
            raise ValidationError('Password must contain one capitalized letter')
        if not (any(ch.isdigit for ch in password.data)):
            raise ValidationError('Password much contain one number')


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()

        if user is None:
            raise ValidationError("That username does not exist in our database.")
        

class UpdateUsernameForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=1, max=40)])
    submit = SubmitField('Update Username')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")


class UpdateProfilePicForm(FlaskForm):
    propic = FileField('Profile Picture', validators=[
        FileRequired(), 
        FileAllowed(['jpg', 'png'], 'Images Only!')
    ])
    submit = SubmitField('Update')
    
class ProposePicForm(FlaskForm):
    new_pic = FileField('Propose Picture', validators=[
        FileRequired(), 
        FileAllowed(['jpg', 'png'], 'Images Only!')
    ])
    breed_name = StringField('Breed')
    submit = SubmitField('Submit')
