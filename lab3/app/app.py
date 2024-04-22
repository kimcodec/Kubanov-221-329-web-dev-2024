from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
import config

app = Flask(__name__)
application = app
app.config.from_object(config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message_category = 'warning'


class User(UserMixin):
    def __init__(self, login, user_id):
        self.user_login = login
        self.id = user_id


def get_users():
    return [
        {"user_id": "1", "login": "admin", "password": "1234"},
    ]


@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if user["user_id"] == user_id:
            return User(user["login"], user["user_id"])
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/counter')
def counter():
    session['counter'] = session.get('counter', 0) + 1
    return render_template('counter.html')


@app.route('/auth', methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        login = request.form['login']
        password = request.form['password']
        remember_me = request.form.get('remember_me', None) == 'on'

        for user in get_users():
            if user["login"] == login and user["password"] == password:
                flash("Logged in successfully", "success")
                login_user(User(login, user["user_id"]), remember_me)
                url_to_redirect = request.args.get('next', url_for('index'))
                return redirect(url_to_redirect)
        flash('Invalid login or password', 'danger')

    return render_template('auth.html')


@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')