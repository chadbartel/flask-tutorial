#!usr/bin/env/python

import os

from flask import Flask


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Run 'hello()' when '/hello' is requested
    @app.route('/hello')
    # Create a simple page that says hello
    def hello():
        return 'Hello, World!'

    from . import db
    # Initialize SQLite database when app is created
    db.init_app(app)

    from . import auth
    # Register 'auth' Blueprint to Flask app
    app.register_blueprint(auth.bp)

    from . import blog
    # Register 'blog' Blueprint to Flask app
    app.register_blueprint(blog.bp)
    # No URL prefix, index view is at '/'
    app.add_url_rule('/', endpoint='index')

    # Return 'Flask' object 'app'
    return app
