from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
#from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '92bb1cc78650ae59ae9b8266bac43d93'
app.config['SECURITY_PASSWORD_SALT']='92bb1cc78650ae59ae9b8266bac43d93'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
mail=Mail(app)
#login_manager = LoginManager(app)
from auth import routes
from auth.routes import auth
app.register_blueprint(auth)