from flask import render_template, url_for, flash, redirect
from flaskblog import app
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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Loggin failed. Please check username or password', 'danger')

    return render_template('login.html', form=form)

