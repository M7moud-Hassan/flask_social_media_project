from flask import render_template, url_for, redirect, flash,Blueprint,request
from .forms import LoginForm,RegisterForm,PostForm
from social_app import app,db,mail,bcrypt,socketio,emit
from .models import Register,Post,Requests,Friends
from .token import generate_confirmation_token,confirm_token
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
from base64 import b64encode
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
    posts=Post.query.all()
    for p in posts:
        if p.privacy==1:
            f=Friends.query.filter_by(friends=p.register_id,register_id=current_user.id)
            if not f:
                posts.remove(p)
        elif p.privacy==3:
            if p.register_id != current_user.id:
                posts.remove(p)
    users=[]
    images=[]
    images_posts=[]
    for p in posts:
        reg=Register.query.filter_by(id=p.register_id).first()
        users.append(reg)
        images.append( b64encode(reg.photo).decode("utf-8"))
        if p.image:
            images_posts.append(b64encode(p.image).decode("utf-8"))
        else:
            images_posts.append("")
    return render_template('home/index.html',
                           title='home',
                           posts=posts,
                           current_user_id=current_user.id,
                           users=users,
                           images_users=images,
                           images_posts=images_posts
                           )

@home.route("/home_post_friends",methods=["GET"])
def home_post_friends():
    posts=Post.query.filter(or_(Post.privacy==1))
    for p in posts:
        f=Friends.query.filter_by(friends=p.register_id,register_id=current_user.id)
        if not f:
            posts.remove(p)
    users=[]
    images=[]
    images_posts=[]
    for p in posts:
        reg=Register.query.filter_by(id=p.register_id).first()
        users.append(reg)
        images.append( b64encode(reg.photo).decode("utf-8"))
        if p.image:
            images_posts.append(b64encode(p.image).decode("utf-8"))
        else:
            images_posts.append("")
    return render_template('home/index.html',
                           title='home',
                           posts=posts,
                           current_user_id=current_user.id,
                           users=users,
                           images_users=images,
                           images_posts=images_posts
                           )

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
                return redirect(url_for('home.home_page'))
       # socketio.emit("reply", "emit successful")
        return render_template('post/add_post.html',title='add post',form=form)
    else:
        return redirect(url_for('auth.index'))
    
@socketio.event
def handle_init_event(data):
        emit("reply", "emit successful")


@home.route("/search",methods=['POST'])
def search():
    if current_user.is_authenticated:
        keyword = request.form.get('search')
        results=Register.query.filter(or_(Register.fName.like("%"+keyword+"%"),Register.lName.like("%"+keyword+"%"))).all()
        for r in results:
            req=Requests.query.filter_by(recive=r.id).first()
            if req:
                results.remove(r)
        if current_user in results:
            results.remove(current_user)
        return render_template('home/friends_search.html',title='home',search=results)
    else:
        return redirect(url_for('auth.index'))

@home.route("/send",methods=['POST'])
def send():
     if current_user.is_authenticated:
        id = request.form.get('id')
        with app.app_context():
            req= Requests(send=current_user.id,recive=id)
            db.session.add(req)
            db.session.commit()
        flash('you send request to friend', 'success')
        return redirect(url_for('home.home_page'))
     else:
        return redirect(url_for('auth.index'))
     
@home.route("/send",methods=['GET'])
def requests():
    if current_user.is_authenticated:
        results=Requests.query.filter_by(recive=current_user.id,status=0)
        friends=[]
        for r in results:
            friends.append(Register.query.filter_by(id=r.send).first())
        return render_template('home/friends_request.html',title='friends',requests=results,friends=friends)
    else:
        return redirect(url_for('auth.index'))

@home.route("/accept",methods=['POST'])
def accept():
    if current_user.is_authenticated:
        id = request.form.get('id')
        with app.app_context():
            req=Requests.query.filter_by(send=current_user.id,recive=id,status=0).first()
            req.status=1
            friend=Friends(register_id=current_user.id,friends=id)
            db.session.add(friend)
            db.session.commit()
            flash('you accept request', 'success')
            return redirect(url_for('home.requests'))
    else:
        return redirect(url_for('auth.index'))
    

@home.route("/reject",methods=['POST'])
def reject():
    if current_user.is_authenticated:
        id = request.form.get('id')
        with app.app_context():
            req=Requests.query.filter_by(recive=current_user.id,send=id).first()
            db.session.delete(req)
            db.session.commit()
            flash('you reject request', 'success')
            return redirect(url_for('home.requests'))
    else:
        return redirect(url_for('auth.index'))

@home.route("/update_post",methods=["POST"])
def update_post():
    if current_user.is_authenticated:
        form=PostForm()
        id = request.form.get('id')
        post=Post.query.filter_by(id=id).first()
        if form.validate_on_submit():
            with app.app_context():
                id = request.form.get('id')
                post=Post.query.filter_by(id=id).first()
                post.des=form.des.data
                post.privacy=form.privacy.data
                pic=request.files['photo']
                if pic:
                    post.image=pic.read()
                db.session.commit()
                flash('update successfull', 'success')
                return redirect(url_for('home.home_page'))
        else:
            return render_template('post/update_post.html',title='add post',form=form,post=post)
       
    else:
        return redirect(url_for('auth.index'))
    
@home.route("/delete_post",methods=["POST"])
def delete_post():
    if current_user.is_authenticated:
        id = request.form.get('id')
        post=Post.query.filter_by(id=id).first()
        if post:
            db.session.delete(post)
            db.session.commit()
            flash('delete successfull', 'success')
            return redirect(url_for('home.home_page'))
    else:
            return redirect(url_for('auth.index'))

@home.route("/profile",methods=["GET"])
def profile():
    if current_user.is_authenticated:
       image=b64encode(current_user.photo).decode("utf-8")
       return render_template('home/profile.html',title='profile',images_user=image)
    else:
       return redirect(url_for('auth.index')) 

@home.route("/update_profile",methods=['POST','GET'])
def update_profile():
    if current_user.is_authenticated:
        with app.app_context():
            current_user.fName=request.form.get('fName')
            current_user.lName=request.form.get('lName')
            current_user.mobile_number=request.form.get('phone')
            current_user.address1=request.form.get('address1')
            current_user.address2=request.form.get('address2')
            current_user.education=request.form.get('education')
            current_user.state=request.form.get('state')
            current_user.Country=request.form.get('country')
            current_user.postcode=request.form.get('postcode')
            pic=request.files['photo']
            if pic:
                current_user.photo=pic.read()
            password=request.form.get('password')
            if password:
                confirm_password=request.form.get('confirm_password')
                if password==confirm_password:
                    current_user.password=hash_password = bcrypt.generate_password_hash(password).decode('utf8')
                else:
                    flash('confirm password not equal to confirm password ','danger')
            db.session.commit()
            return redirect(url_for('home.profile')) 
    else:
        return redirect(url_for('auth.index')) 