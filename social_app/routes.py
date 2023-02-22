from flask import render_template, url_for, redirect, flash,Blueprint,request
from .forms import LoginForm,RegisterForm,PostForm
from social_app import app,db,mail,bcrypt,socketio,emit
from .models import Register,Post
from .token import generate_confirmation_token,confirm_token
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint(
	'auth',
	__name__,
	url_prefix='/auth'
)
home = Blueprint(
	'home',
	__name__,
	url_prefix='/home'
)

@auth.route('/index',methods=["GET","POST"])
@auth.route('/',methods=["GET","POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home.home_page'))
    form=LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            register = Register.query.filter_by(email=form.email.data).first()
            if register is not None and bcrypt.check_password_hash(register.password,form.password.data):
                if register.is_active:
                    flash(f"Login Successfull {form.email.data}", "success")
                    login_user(register)
                    return redirect(url_for('home.home_page'))
                else:
                      flash(f"please verify email", "danger")
            else:
                flash(f"password erorr  or user name", "danger")
    return render_template('auth/index.html',title='index',form=form)	

@auth.route('/register',methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.home_page'))
    form=RegisterForm()
    if form.validate_on_submit():
        with app.app_context():
            pic=request.files['photo']
            if pic:
                hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
                register=Register(fName=form.fName.data,lName=form.lName.data,email=form.email.data,
                                password=hash_password,is_active=False,photo=pic.read())
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

@auth.route('/confirm/<token>',methods=["GET","POST"])
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.home_page'))
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    register=Register.query.filter_by(email=email).first()
    if register.is_active:
         flash('Account already confirmed. Please login.', 'success')
    else:
            register.is_active=True
            db.session.add(register)
            db.session.commit()
            flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.index'))

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender='soonfu0@gmail.com'
    )
    mail.send(message=msg)

@home.route("/home_page",methods=["GET","POST"])
def home_page():
    return render_template('home/index.html',title='home')

@home.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.index'))

@home.route("/add_post",methods=["GET","POST"])
def add_post():
    if current_user.is_authenticated:
        form=PostForm()
        if form.validate_on_submit():
            with app.app_context():
                pic=request.files['photo']
                if pic:
                    post=Post(image=pic.read(),des=form.des.data,privacy=form.privacy.data,register_id=current_user.id)
                    db.session.add(post)
                    db.session.commit()
                else:
                    post=Post(des=form.des.data,privacy=form.privacy.data,register_id=current_user.id)
                    db.session.add(post)
                    db.session.commit()
        socketio.emit("reply", "emit successful")
        return render_template('post/add_post.html',title='add post',form=form)
    else:
        return redirect(url_for('auth.index'))
    
@socketio.event
def handle_init_event(data):
        emit("reply", "emit successful")
       