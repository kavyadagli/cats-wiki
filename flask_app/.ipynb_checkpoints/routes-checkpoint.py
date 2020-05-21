# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response, send_file
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from PIL import Image

from flask_mail import Message

# stdlib
from datetime import datetime
import io
import base64

# local
from . import app, bcrypt, client, mail
from .forms import (SearchForm, CatReviewForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from .models import User, Review, load_user
from .utils import current_time

""" ************ View functions ************ """
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('query_results', query=form.search_query.data))

    return render_template('index.html', form=form)

@app.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client.search(query)

    if type(results) != list:

        return render_template('query.html', error_msg='Error')
    elif len(results) == 0:
        return render_template('query.html', error_msg='Error')

    #return str(results)
    return render_template('query.html', results=results)

@app.route('/cats/<cat_name>', methods=['GET', 'POST'])
def cat_detail(cat_name):
    attributes_to_keep = ['affection_level', 'child_friendly', 'dog_friendly', 'energy_level', 'grooming', 'hypoalergenic']

    #temp = client.retrieve_cat_by_id(cat_name)
    #return str(temp)

    image_result, breed_result = client.retrieve_cat_by_id(cat_name)
    ratings = dict()
    for key in breed_result[0].keys():
        value = str(breed_result[0][key])
        if value.isdigit() and key in attributes_to_keep:
            new_key = key.replace('_', ' ').capitalize()
            ratings[new_key] = (range(int(value)), range(5-int(value)))
    #return str(temp)
    #return str(image_result)

    #if type(image_result) == dict:
    #    return render_template('movie_detail.html', error_msg=result['Error'])
    
    if len(image_result) == 0 or len(breed_result) == 0:
        return render_template('movie_detail.html', error_msg="error")

    form = CatReviewForm()
    if form.validate_on_submit():
        review = Review(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            #########
            cat_name=cat_name,
            #movie_title=result.title
        )

        
        review.save()
        

        return redirect(request.path)

    reviews_m = Review.objects(cat_name=cat_name)
    reviews = []
    for r in reviews_m:
        reviews.append({
            'date': r.date,
            'username': r.commenter.username,
            'content': r.content,
            'image': images(r.commenter.username)
        })

    #return str(image_result[0])
    return render_template('movie_detail.html', form=form, image=image_result[0], cat=breed_result[0], ratings=ratings, reviews=reviews)

@app.route('/user/<username>')
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    image = images(username)

    return render_template('user_detail.html', username=username, reviews=reviews, image=image)

# @app.route('/images/<username>.png')
def images(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image


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
