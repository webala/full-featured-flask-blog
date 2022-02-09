from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import app, db
from .models import User, Post
from .forms import RegistrationForm, LoginForm

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
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

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
    if current_user.is_authenticated:
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


@app.route('/account')
@login_required
def account():
    return render_template('account.html')
