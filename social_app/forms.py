from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField,SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from .models import Register
class RegisterForm(FlaskForm):
    fName= StringField(
		'first name',
		validators=[
			DataRequired(),
			Length(max=30)
		]
	)
    lName= StringField(
		'last name',
		validators=[
			DataRequired(),
			Length(max=30)
		]
	)
    email = StringField(
		'Email',
		validators=[
			DataRequired(),
			Email()
		]
	)
    password = PasswordField(
		'Password',
		validators=[
			DataRequired()
		]
	)
    confirm_password = PasswordField(
		'Confirm Password',
		validators=[
			DataRequired(),
			EqualTo('password')
		]
	)
    submit = SubmitField(
		'Sign Up'
	)
    def validate_email(self, email):
        register = Register.query.filter_by(email=email.data).first()
        if register:
            raise ValidationError('Email already exists')

class LoginForm(FlaskForm):
	email = StringField(
		'Email',
		validators=[
			DataRequired(),
			Email()
		]
	)
	password = PasswordField(
		'Password',
		validators=[
			DataRequired()
		]
	)
	submit = SubmitField(
		'LogIn'
	)

class PostForm(FlaskForm):
	des= TextAreaField(
		'description',
		validators=[
			DataRequired(),
			Length(max=500)
		]
	)
	privacy=SelectField(u'select privacy', choices=[(1, 'friends'), (2, 'Public'), (3, 'only me')])
	submit = SubmitField(
		'Push'
	)