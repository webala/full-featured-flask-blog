from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_login import login_required, current_user
from flaskblog import db
from .models import Post
from .forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route('/post/new', methods=(['GET', 'POST']))
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', form=form)

@posts.route('/post/<int:post_id>', methods=(['GET', 'POST']))
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm ()
    
    if post.author == current_user and form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET': # To avoid populating the form data on a post request
        form.title.data = post.title
        form.content.data = post.content

    return render_template('post.html', post=post, form=form)

@posts.route('/post/<int:post_id>/delete', methods=(['POST']))
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.home'))