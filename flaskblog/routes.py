import secrets
import os
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import app, db
from .models import User, Post
from .forms import RegistrationForm, LoginForm, UpdateAccountForm

posts = [
    {
        'author': 'COrey Schafer',
        'title': 'Blog post',
        'content': 'First post content',
        'date_posted': '1st August 2020'
    },
    {
        'author': 'COrey Schafer',
        'title': 'Blog post',
        'content': 'First post content',
        'date_posted': '1st August 2020'
    },
    {
        'author': 'COrey Schafer',
        'title': 'Blog post',
        'content': 'First post content',
        'date_posted': '1st August 2020'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        

        user = User(
            username= form.username.data,
            email = form.email.data,
        )
        user.password = user.generate_password_hash(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}. You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated: # using the user loader defined in models.py
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password_hash(form.password.data):

            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Loggin failed. Please check email or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename) # uploaded files have filename attribute. The unserscore is the filename(underscore since we won't use it)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    form_picture.save(picture_path)
    return picture_filename


@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/{}'.format(current_user.image_file))

    form = UpdateAccountForm()
    if form.validate_on_submit():
        
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account')) # Because of post get redirect pattern (Prevent resubmission of data)
    elif request.method == 'GET': #populate form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('account.html', image_file=image_file, form=form)
