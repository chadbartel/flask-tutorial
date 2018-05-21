#!usr/bin/env/python

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


# Create a database connection stored in 'g'
def get_db():
    if 'db' not in g:
        # Establish connection to 'DATABASE' config key
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows like 'dict' data types
        g.db.row_factory = sqlite3.Row

    # Return a connection to SQLite database
    return g.db


# Close database connection if it exists
def close_db(e=None):
    # Get value of 'db' from 'g'
    db = g.pop('db', None)

    # Check if 'db' exists
    if db is not None:
        # 'db' exists, close
        db.close()


# Initialize the site database
def init_db():
    # Get a database connection
    db = get_db()

    # Open the 'schema.sql' file relative to 'flaskr' package
    with current_app.open_resource('schema.sql') as f:
        # Run the 'schema.sql' file
        db.executescript(f.read().decode('utf8'))


# Create 'init-db' command to be used with "flask"
@click.command('init-db')
@with_appcontext
# Define function to run when 'init-db' command is called
def init_db_command():
    # Call 'init_db()' function to initialize site database
    init_db()
    # Communicate site database has been successfully initialized
    click.echo('Initialized the database.')


def init_app(app):
    # Call 'close_db()' after returning the response
    app.teardown_appcontext(close_db)
    # Add command 'init_db_command' (alias 'init-db') to Flask app
    app.cli.add_command(init_db_command)
