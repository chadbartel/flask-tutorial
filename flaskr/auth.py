#!usr/bin/env/python

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# Create Blueprint object named 'auth'
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Associate URL "/register" with 'register()'
@bp.route('/register', methods=('GET', 'POST'))
# Return 'register' view when received request to '/auth/register'
def register():
    # Check if the requested page's class is "post"
    if request.method == 'POST':
        # Get value of 'username' from request's form
        username = request.form['username']
        # Get value of 'password' from request's form
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            # Username field is empty
            error = 'Username is required.'
        elif not password:
            # Password field is empty
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            # Username already exists in database
            error = 'User {} is already registered.'.format(username)

        if error is None:
            # Username and password has been validated and will be saved
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # Redirect user to login URL
            return redirect(url_for('auth.login'))

        # Form validation did not pass, show error message to user
        flash(error)

    # Render HTML template to user for the register page
    return render_template('auth/register.html')


# Associate URL "/login" with 'login()'
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # Check if the requested page's class is "post"
    if request.method == 'POST':
        # Get value of 'username' from request's form
        username = request.form['username']
        # Get value of 'password' from request's form
        password = request.form['password']
        # Get a connection to SQLite database
        db = get_db()
        error = None
        # Get the user's record from the 'user' table
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            # The 'user' select statement did not return a record
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            # The submitted password hash does not match the stored password hash
            error = 'Incorrect password.'

        # Login is successful
        if error is None:
            # Clear data from the users session
            session.clear()
            # Create a new session for the validated user
            session['user_id'] = user['id']
            # Redirect user to index URL
            return redirect(url_for('index'))

        # Form validation did not pass, show error message to user
        flash(error)

    # Render HTML template to user for the login page
    return render_template('auth/login.html')


# Register 'load_logged_in_user()' to trigger before the 'view' function
@bp.before_app_request
def load_logged_in_user():
    # Get user from current session
    user_id = session.get('user_id')

    if user_id is None:
        # User is not in the current session
        g.user = None
    else:
        # User is in the current session, get user's data from database
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# Associate URL "/logout" with 'logout()'
@bp.route('/logout')
def logout():
    # Remove user id from session
    session.clear()
    # Redirect user to the index page
    return redirect(url_for('index'))


# Function to request login details from user
def login_required(view):
    # Allows 'login_required()' to be applied to any view
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # User is not logged in
        if g.user is None:
            # Redirect user to the login page
            return redirect(url_for('auth.login'))

        # User is logged in, return the view
        return view(**kwargs)

    # Return new view function wrapping original view it's applied to
    return wrapped_view
