# 3rd-party packages
from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash, Response, send_file
from flask_mongoengine import MongoEngine

# local
from flask_app import description

description = Blueprint('description', __name__, url_prefix='/')
""" ************ View functions ************ """
@description.route('/site_description')
def site_description():
    return render_template('site_description.html')
