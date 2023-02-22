from social_app import db,login_manager
from flask_login import UserMixin
@login_manager.user_loader
def load_user(register_id):
	return Register.query.get(int(register_id))


class Register(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    fName=db.Column(db.String(30),nullable=False)
    lName=db.Column(db.String(30),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    is_active=db.Column(db.Boolean,default=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.Text,nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
	    return f"{self.fName} {self.lName}"

class Post(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	image = db.Column(db.Text,nullable=True)
	des= db.Column(db.String(500),nullable=True)
	privacy=db.Column(db.Integer,nullable=False)
	register_id = db.Column(db.db.Integer, db.ForeignKey('register.id'), nullable=False)