from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO, emit

bcrypt = Bcrypt()

app = Flask(__name__)

app.config['SECRET_KEY'] = '92bb1cc78650ae59ae9b8266bac43d93'
app.config['SECURITY_PASSWORD_SALT']='92bb1cc78650ae59ae9b8266bac43d93'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'soonfu0@gmail.com',
    MAIL_PASSWORD = 'ezjbcoviunkpwsdw',
))
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app,metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)
mail=Mail(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
from social_app import routes
from social_app.routes import auth,home
app.register_blueprint(auth)
app.register_blueprint(home)