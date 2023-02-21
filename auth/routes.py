from flask import render_template, url_for, redirect, flash,Blueprint,request
from .forms import LoginForm,RegisterForm
from auth import app,db,mail
from .models import Register
from .token import generate_confirmation_token,confirm_token
from flask_mail import Message

auth = Blueprint(
	'auth',
	__name__,
	url_prefix='/auth'
)

@auth.route('/index')
@auth.route('/')
def index():
    form=LoginForm()
    return render_template('auth/index.html',title='index',form=form)	

@auth.route('/register',methods=["GET","POST"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        with app.app_context():
            pic=request.files['photo']
            if pic:
                register=Register(fName=form.fName.data,lName=form.lName.data,email=form.email.data,
                                password=form.password.data,is_active=False,photo=pic.read())
                db.session.add(register)
                db.session.commit()
                token = generate_confirmation_token(form.email.data)
                confirm_url = url_for('auth.confirm_email', token=token, _external=True)
                html = render_template('auth/confirm_email.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(form.email.data, subject, html)
                flash('A confirmation email has been sent via email.', 'success')
                return redirect(url_for('auth.index'))
    return render_template('auth/register.html',title='register',form=form)

@auth.route('/confirm/<token>')
def confirm_email(token):
    email=""
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    register=Register.query.filter(email=email).first()
    if register.is_active:
         flash('Account already confirmed. Please login.', 'success')
    else:
        with app.app_context():
            register.is_active=True
            db.session.add(register)
            db.session.commit()
            flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender='soonfu0@gmail.com'
    )
    mail.send(message=msg)