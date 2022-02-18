from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from .models import User
from .utils import send_reset_email, save_picture
from flaskblog.posts.models import Post

users = Blueprint('users', __name__)


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

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
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated: # using the user loader defined in models.py
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password_hash(form.password.data):

            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Loggin failed. Please check email or password', 'danger')

    return render_template('login.html', form=form)

@users.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))

@users.route('/account/<username>', methods=['POST', 'GET'])
@login_required
def account(username):
    
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for('static', filename='profile_pics/{}'.format(user.image_file))
    posts = Post.query.order_by(Post.date_posted.desc()).filter_by(author=user)

    
    if user == current_user:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated', 'success')
            return redirect(url_for('users.account', username=user.username)) # Because of post get redirect pattern (Prevent resubmission of data)

        elif request.method == 'GET': #populate form with current user data
            form.username.data = current_user.username
            form.email.data = current_user.email
    else:
        form = None

    return render_template('account.html', image_file=image_file, form=form, posts=posts, user=user)

@users.route('/reset_password', methods=(['POST', 'GET']))
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)

@users.route('/reset_password/<token>', methods=(['POST', 'GET']))
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)

    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password = user.generate_password_hash(form.password.data)
        db.session.commit()

        flash('Your password has been updated! You can now login.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)