# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)

# stdlib
import os
from datetime import datetime

# local
from .client import CatClient

import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://heroku_62h2lcbv:hq81vpbtmn5lvg42nu2mbnlcvo@ds163020.mlab.com:63020/heroku_62h2lcbv"
app.config['MONGODB_HOST'] = 'mongodb://localhost:27017/final'
#app.config['SECRET_KEY'] = b'\x020;yr\x91\x11\xbe"\x9d\xc1\x14\x91\xadf\xec'
app.config['SECRET_KEY'] = os.urandom(16)

csp = {
    'default-src': '*',
    'img-src': 
        ['data:', 
        '*'
        ],
    'style-src':
        ['\'unsafe-inline\' \'self\'',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css'
        ],
    'script-src': 
        ['\'unsafe-inline\' \'self\'',
            'https://code.jquery.com/jquery-3.4.1.slim.min.js', 
            'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
            'https://code.jquery.com/jquery-3.4.1.slim.min.js',
            'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js'        
        ],
    "content_security_policy": "style-src 'unsafe-inline'" 
}

Talisman(app, 
    content_security_policy=csp,
    content_security_policy_report_uri='/csp_reports' 
)

# mongo = PyMongo(app)
db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'catwiki388j@gmail.com',
    MAIL_PASSWORD = 'cmsc388j',
))
mail = Mail(app)

from flask_app.features.routes import features
from flask_app.users.routes import users
from flask_app.description.routes import description

app.register_blueprint(users)
app.register_blueprint(features)
app.register_blueprint(description)
