from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

from app import db_connector
from psycopg.rows import namedtuple_row
from users_policy import UsersPolicy

bp = Blueprint('auto', __name__, url_prefix='/auto')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth'
    login_manager.login_message = 'Пройдите авторизацию для доступа к этому ресурсу'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)


class User(UserMixin):
    def __init__(self, user_id, user_login, role_id):
        self.id = user_id
        self.user_login = user_login
        self.role_id = role_id

    def is_admin(self):
        return self.role_id == current_app.config['ADMIN_ROLE_ID']

    def can(self, action, user=None):
        policy = UsersPolicy(user)
        return getattr(policy, action, lambda: False)()


def load_user(user_id):
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        cursor.execute("SELECT id, login, role_id FROM users WHERE id = %s;", (user_id,))
        user = cursor.fetchone()
    if user is not None:
        return User(user.id, user.login, user.role_id)
    return None


def check_for_privelege(action):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            user = None
            if 'user_id' in kwargs.keys():
                with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s;", (kwargs.get('user_id'),))
                    user = cursor.fetchone()
            if not (current_user.is_authenticated and current_user.can(action, user)):
                flash('Недостаточно прав для доступа к этой странице', 'warning')
                return redirect(url_for('users.index'))
            return function(*args, **kwargs)

        return wrapper

    return decorator


@bp.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']
        remember_me = request.form.get('remember_me', None) == 'on'
        with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
            cursor.execute(
                "SELECT id, login, role_id FROM users WHERE login = %s AND password_hash = CAST(SHA256(%s) AS VARCHAR)",
                (login, password)
            )
            user = cursor.fetchone()

            if user:
                flash('Авторизация прошла успешно', 'success')
                login_user(User(user.id, user.login, user.role_id), remember=remember_me)
                next_url = request.args.get('next', url_for('index'))
                return redirect(next_url)
            flash('Invalid username or password', 'danger')
    return render_template('auth.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
