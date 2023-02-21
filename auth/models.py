from auth import db
class Register(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    fName=db.Column(db.String(30),nullable=False)
    lName=db.Column(db.String(30),nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    is_active=db.Column(db.Boolean,default=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.Text,nullable=False)

    def __repr__(self):
	    return f"{self.fName} {self.lName}"