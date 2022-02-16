import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flaskblog import app, db, mail
from .models import User, Post
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm



@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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

    #Resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_filename


@app.route('/account/<username>', methods=['POST', 'GET'])
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
            return redirect(url_for('account', username=user.username)) # Because of post get redirect pattern (Prevent resubmission of data)

        elif request.method == 'GET': #populate form with current user data
            form.username.data = current_user.username
            form.email.data = current_user.email
    else:
        form = None

    return render_template('account.html', image_file=image_file, form=form, posts=posts, user=user)

@app.route('/post/new', methods=(['GET', 'POST']))
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title = form.title.data,
            content = form.content.data,
            author = current_user # The back reference can be used instead of the user id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

@app.route('/post/<int:post_id>', methods=(['GET', 'POST']))
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm ()
    
    if post.author == current_user and form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET': # To avoid populating the form data on a post request
        form.title.data = post.title
        form.content.data = post.content

    return render_template('post.html', post=post, form=form)

@app.route('/post/<int:post_id>/delete', methods=(['POST']))
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset Request', #Subject
            sender = 'noreply@demo.com',
            recipients = [user.email]
    )

    msg.body = f'''
To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)} 

If you did not make this request then simply ignore this email and no changes will be made.
'''#external is used in order to get an absolute url not a relative url. Link in email should have full domain
    mail.send(msg)


@app.route('/reset_password', methods=(['POST', 'GET']))
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)

@app.route('/reset_password/<token>', methods=(['POST', 'GET']))
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)

    if not user:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password = user.generate_password_hash(form.password.data)
        db.session.commit()

        flash('Your password has been updated! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)