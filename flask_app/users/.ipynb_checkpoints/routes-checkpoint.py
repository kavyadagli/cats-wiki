# 3rd-party packages
from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, Response, send_file
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from PIL import Image
from flask_mail import Message

# stdlib
import io
import base64

# local
from flask_app import app, bcrypt, client, mail
from flask_app.forms import (RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from flask_app.models import User, load_user


users = Blueprint('users', __name__)

""" ************ User Management views ************ """
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():

        msg = Message('Thanks for Registering!', sender = 'catwiki388j@gmail.com', recipients = [str(form.email.data)])
        msg.body = "Hi there! Thanks for registering to Cat Wiki!\n\nYour username is: "+str(form.username.data)+"\n\nThank you for using our website, we hope you have an excellent day!"
        mail.send(msg)
        
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()

        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('account'))
        else:
            flash('Login failed. Check your username and/or password')
            return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    username_form = UpdateUsernameForm()
    profile_pic_form = UpdateProfilePicForm()

    if username_form.validate_on_submit():
        # current_user.username = username_form.username.data
        
        temp = User.objects(username=current_user.username).first()
        
        
        msg = Message('Username Change', sender = 'catwiki388j@gmail.com', recipients = [str(temp.email)])
        msg.body = "Your username has been updated!\nYour new username is: "+str(username_form.username.data)
        mail.send(msg)
        
        current_user.modify(username=username_form.username.data)
        current_user.save()
        
        return redirect(url_for('account'))

    if profile_pic_form.validate_on_submit():
        img = profile_pic_form.propic.data
        filename = secure_filename(img.filename)

        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(img.stream, content_type='images/png')
        else:
            current_user.profile_pic.replace(img.stream, content_type='images/png')
        current_user.save()

        return redirect(url_for('account'))

    image = images(current_user.username)

    return render_template("account.html", title="Account", username_form=username_form, profile_pic_form=profile_pic_form, image=image)

def images(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image
