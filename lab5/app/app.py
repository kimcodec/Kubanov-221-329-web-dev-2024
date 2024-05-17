from flask import Flask, render_template, session, request
from flask_login import current_user, login_required

import psycopg
from psycopg.rows import namedtuple_row
from postgres import DBConnector

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db_connector = DBConnector(app)

from auth import bp as auto_bp, init_login_manager

app.register_blueprint(auto_bp)
init_login_manager(app)

from users import bp as users_bp

app.register_blueprint(users_bp)

from user_actions import bp as user_actions_bp

app.register_blueprint(user_actions_bp)


@app.before_request
def record_action():
    if request.endpoint == 'static':
        return
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        try:
            user_id = current_user.id if current_user.is_authenticated else None
            path = request.path
            query = "INSERT INTO user_actions (user_id, path) VALUES (%s, %s)"
            cursor.execute(query, (user_id, path))
            db_connector.connect().commit()
        except psycopg.Error as ex:
            db_connector.connect().rollback()
            app.logger.error(ex)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')


@app.route('/counter')
def counter():
    session['counter'] = session.get('counter', 0) + 1
    return render_template('counter.html')