from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)
app.config['SECRET_KEY'] = '1a72248ba5f91ffed1b7bb9651f10ebf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app) # encrypts password

login_manager = LoginManager(app) # manages user sessions
login_manager.login_view = 'login' 
login_manager.login_message_category = 'info'

from flaskblog import routes