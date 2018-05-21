#!usr/bin/env/python

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

# Create the 'blog' Blueprint object
bp = Blueprint('blog', __name__)


# Associate URL "/register" with 'index()'
@bp.route('/')
def index():
    # Get a connection to SQLite database
    db = get_db()
    # Query SQLite database for all blog posts, most recent first, with JOIN on user's posts
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# Associate URL "/create" with 'create()'
@bp.route('/create', methods=('GET', 'POST'))
# Call 'login_required()' function for '/create' view to be accessed
@login_required
def create():
    # Check if the requested page's class is "post"
    if request.method == 'POST':
        # Get value of 'title' from request's form
        title = request.form['title']
        # Get value of 'body' from request's form
        body = request.form['body']
        error = None

        if not title:
            # User did not provide a title for their post
            error = 'Title is required.'

        if error is not None:
            # Show the error produced to the user
            flash(error)
        else:
            # Get a connection to SQLite database
            db = get_db()
            # Add the new blog post to SQLite database
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            # Redirect user to the main blog view
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


# Define function to get a post by 'id'
def get_post(id, check_author=True):
    post = get_db().execute(
        # Query SQLite database for a post's information by 'id'
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        # There is no post by the id value passed; raise HTTP status 404
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        # User is not the author of the post; raise HTTP status 403
        abort(403)

    return post


# Associate URL "/post's id/update" with 'update()'
# Get post's id from URL and pass to function 'update()'
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
# Call 'login_required()' function for '/update' view to be accessed
@login_required
def update(id):
    # Get the post by 'id' to be updated
    post = get_post(id)

    # Check if the requested page's class is "post"
    if request.method == 'POST':
        # Get value of 'title' from request's form
        title = request.form['title']
        # Get value of 'body' from request's form
        body = request.form['body']
        error = None

        if not title:
            # User did not provide a title for their post
            error = 'Title is required.'

        if error is not None:
            # Show the error produced to the user
            flash(error)
        else:
            # Get a connection to SQLite database
            db = get_db()
            # Update the existing blog post in SQLite database
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # Redirect user to the main blog view
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# Associate URL "/post's id/delete" with 'delete()'
@bp.route('/<int:id>/delete', methods=('POST',))
# Call 'login_required()' function for '/delete' view to be accessed
@login_required
def delete(id):
    # Get the post by 'id' to be updated
    get_post(id)
    # Get a connection to SQLite database
    db = get_db()
    # Delete the post's record from SQLite database
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    # Redirect user to the main blog view
    return redirect(url_for('blog.index'))
