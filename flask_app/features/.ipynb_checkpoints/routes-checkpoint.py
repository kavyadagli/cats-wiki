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
from datetime import datetime
import io
import base64
import sys
import json

# local

from flask_app import features, bcrypt, mail
from flask_app.client import CatClient
from flask_app.forms import (SearchForm, CatReviewForm, ProposePicForm)
from flask_app.models import User, Review, load_user, CatImage
from flask_app.utils import current_time

features = Blueprint('features', __name__, url_prefix='/')
""" ************ View functions ************ """
@features.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    print('FELL INTO VIEW', file=sys.stdout)
    if form.validate_on_submit():
        # return redirect(url_for('query_results', query=form.search_query.data))
        print('FELL INTO VALIDATE FORM', file=sys.stdout)
        return redirect(url_for('features.query_results', query=form.search_query.data))
    return render_template('index.html', form=form)

@features.route('/csp_report')
def csp_report():
    return json.loads(request.data.decode())["csp-report"]

@features.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    client = CatClient()
    results = client.search(query)

    if type(results) != list:
        return render_template('query.html', error_msg='Error')
    elif len(results) == 0:
        return render_template('query.html', error_msg='Error')

    return render_template('query.html', results=results)

@features.route('/cats/<cat_name>', methods=['GET', 'POST'])
def cat_detail(cat_name):
    client = CatClient()
    attributes_to_keep = ['affection_level', 'child_friendly', 'dog_friendly', 'energy_level', 'grooming', 'hypoalergenic']

    image_result, breed_result = client.retrieve_cat_by_id(cat_name)
    ratings = dict()
    for key in breed_result[0].keys():
        value = str(breed_result[0][key])
        if value.isdigit() and key in attributes_to_keep:
            new_key = key.replace('_', ' ').capitalize()
            ratings[new_key] = (range(int(value)), range(5-int(value)))

    #if type(image_result) == dict:
    #    return render_template('movie_detail.html', error_msg=result['Error'])

    if len(image_result) == 0 or len(breed_result) == 0:
        return render_template('cat_detail.html', error_msg="error")

    picform = ProposePicForm()
    print(picform.errors)
    if picform.validate_on_submit():
        temp = User.objects(username=current_user.username).first()
        msg = Message('Upload Request', sender = 'catwiki388j@gmail.com', recipients = [str(temp.email)])
        msg.body = "Thanks for requesting to upload an image to breed:"+str(cat_name)+ "!\nYour image is attached to this email"
        msg.attach(
            picform.new_pic.data.filename,
            'images/png',
            picform.new_pic.data.read())
        mail.send(msg)
        
        msg = Message('Upload Request', sender = 'catwiki388j@gmail.com', recipients = ['catwiki388j@gmail.com'])
        msg.body = "Someone is requesting to upload image to breed: "+str(cat_name)
        msg.attach(
            picform.new_pic.data.filename,
            'images/png',
            picform.new_pic.data.read())
        mail.send(msg)
        
        img = picform.new_pic.data
        filename = secure_filename(img.filename)

        pim = CatImage(
            commenter=load_user(current_user.username),
            date = current_time(),
            im = None,
            cat_name = cat_name,
        )
        pim.save()
        pim.im.put(img.stream, content_type='images/png')
        pim.save()

        return redirect(url_for('features.cat_detail',cat_name=cat_name))



    form = CatReviewForm()
    print(form.text.data)
    print(form.errors)
    if form.validate_on_submit():
        review = Review(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            cat_name=cat_name,
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

    return render_template('cat_detail.html', form=form, image=image_result[0], cat=breed_result[0], ratings=ratings, reviews=reviews, picform=picform)

@features.route('/user/<username>')
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)
    pim = CatImage.objects(commenter=user)
    image = images(username)

    proposed = {}
    for p in pim:
        bytes_im = io.BytesIO(p['im'].read())
        img = base64.b64encode(bytes_im.getvalue()).decode()
        print(img)
        proposed[p['cat_name']] = img
    print(proposed, file=sys.stdout)
    return render_template('user_detail.html', username=username, reviews=reviews, image=image, pim=proposed)

def images(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image
