import re
import psycopg
from psycopg.rows import namedtuple_row
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from postgres import DBConnector

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db_connector = DBConnector(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'
login_manager.login_message = 'Пройдите авторизацию для доступа к этому ресурсу'
login_manager.login_message_category = 'warning'


class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.user_login = user_login


def get_roles():
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        cursor.execute("SELECT * FROM roles")
        return cursor.fetchall()


@login_manager.user_loader
def load_user(user_id):
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        cursor.execute("SELECT id, login FROM users WHERE id = %s;", (user_id,))
        user = cursor.fetchone()
    if user is not None:
        return User(user.id, user.login)
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        login = request.form['username']
        password = request.form['password']
        remember_me = request.form.get('remember_me', None) == 'on'
        with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
            cursor.execute(
                "SELECT id, login FROM users WHERE login = %s AND password_hash = CAST(SHA256(%s) AS VARCHAR)",
                (login, password)
            )
            user = cursor.fetchone()
            app.logger.info(msg=user)

            if user:
                flash('Авторизация прошла успешно', 'success')
                login_user(User(user.id, user.login), remember=remember_me)
                next_url = request.args.get('next', url_for('index'))
                return redirect(next_url)
            flash('Invalid username or password', 'danger')
    return render_template('auth.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/counter')
def counter():
    session['counter'] = session.get('counter', 0) + 1
    return render_template('counter.html')


@app.route('/users')
def users():
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        cursor.execute("SELECT users.*, roles.name AS role FROM users LEFT JOIN roles ON users.role_id = roles.id")
        users = cursor.fetchall()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def users_delete(user_id):
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        db_connector.connect().commit()
        flash('Учетная запись успешно удалена', 'success')
    return redirect(url_for('users'))


def validate_login(login):
    errors = []
    if not login:
        return ['Логин не может быть пустым']
    if len(login) < 5:
        errors.append("Логин должен быть длиннее 5 символов")
    if not login or not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]+$", login):
        errors.append("Логин должен быть состоять только из букв и цифр")
    return errors


def validate_password(password):
    errors = []
    if not password:
        return ['Пароль не может быть пустым']
    if len(password) < 8 or len(password) > 128:
        errors.append("Пароль должен содержать от 8 до 128 символов")
    if not re.search(r"[a-z]", password):
        errors.append("Пароль должен содержать хотя бы одну строчную букву")
    if not re.search(r"[A-Z]", password):
        errors.append("Пароль должен содержать хотя бы одну заглавную букву")
    if not re.search(r"\d", password):
        errors.append("Пароль должен содержать хотя бы одну цифру")
    if not re.search(r"[~!@#$%^&*_\-+=()\[\]{}><\\/|\"'.,:;]", password):
        errors.append("Пароль должен содержать хотя бы один специальный символ")

    return errors


def validate_name(name):
    errors = []
    if name is None or len(name) == 0:
        errors.append("Имя не должно быть пустым")

    return errors


@app.route('/users/new', methods=['POST', 'GET'])
@login_required
def users_new():
    user_data = {}
    errors = {}
    if request.method == 'POST':
        fields = ('login', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form[field] or None for field in fields}
        errors['login'] = validate_login(user_data['login'])
        errors['password'] = validate_password(user_data['password'])
        errors['first_name'] = validate_name(user_data['first_name'])
        errors['last_name'] = validate_name(user_data['last_name'])
        if errors['login'] or errors['password'] or errors['first_name'] or errors['last_name']:
            return render_template(
                'users_new.html',
                user_data=user_data,
                roles=get_roles(),
                errors=errors
            )
        with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
            try:
                query = str("INSERT INTO users (login, password_hash, first_name, middle_name, last_name, role_id) "
                            "VALUES (%(login)s, CAST(SHA256(%(password)s) AS varchar), %(first_name)s, %(middle_name)s,"
                            "%(last_name)s, %(role_id)s)")
                cursor.execute(query, user_data)
                db_connector.connect().commit()
                flash('Учетная запись успешно создана', 'success')
                return redirect(url_for('users'))
            except psycopg.Error:
                flash('Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены', 'danger')
    return render_template('users_new.html', user_data=user_data, roles=get_roles(), errors={})


@app.route('/users/<int:user_id>/view')
def users_view(user_id):
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, [user_id])
        user_data = cursor.fetchone()
        if not user_data:
            flash('Пользователя нет в базе данных', 'danger')
            return redirect(url_for('users'))
        query = "SELECT name FROM roles WHERE id = %s"
        cursor.execute(query, [user_data.role_id])
        user_role = cursor.fetchone()
    return render_template('users_view.html', user_data=user_data, user_role=user_role.name)


@app.route('/users/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
def users_edit(user_id):
    errors = {}
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        query = ("SELECT first_name, middle_name, last_name, role_id "
                 "FROM users WHERE id = %s")
        cursor.execute(query, [user_id])
        user_data = cursor.fetchone()
        if not user_data:
            flash('Пользователя нет в базе данных', 'danger')
            return redirect(url_for('users'))
        if request.method == 'POST':
            fields = ('first_name', 'middle_name', 'last_name', 'role_id')
            user_data = {field: request.form[field] or None for field in fields}
            errors['first_name'] = validate_name(user_data['first_name'])
            errors['last_name'] = validate_name(user_data['last_name'])
            if errors['first_name'] or errors['last_name']:
                return render_template(
                    'users_edit.html',
                    user_data=user_data,
                    roles=get_roles(),
                    errors=errors
                )
            user_data['id'] = user_id
            try:
                query = ("UPDATE users SET first_name = %(first_name)s, "
                         "middle_name = %(middle_name)s, last_name = %(last_name)s, "
                         "role_id = %(role_id)s WHERE id = %(id)s")
                cursor.execute(query, user_data)
                db_connector.connect().commit()
                flash('Учетная запись успешно изменена', 'success')
                return redirect(url_for('users'))
            except psycopg.Error:
                flash('Произошла ошибка при изменении записи.', 'danger')
    return render_template('users_edit.html', user_data=user_data, roles=get_roles())


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    errors = {}
    if request.method == 'POST':
        user_id = current_user.id
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if confirm_password != new_password:
            errors['confirm_password'] = ['Пароли должны совпадать']
        with db_connector.connect().cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s AND password_hash = CAST(SHA256(%s) AS VARCHAR)",
                           (user_id, old_password))
            if not cursor.fetchone():
                errors['old_password'] = ['Введён неверный пароль']

            errors['new_password'] = validate_password(new_password)

            if not errors['new_password'] and not errors['new_password']:
                cursor.execute("UPDATE users SET password_hash = CAST(SHA256(%s) AS VARCHAR) WHERE id = %s",
                               (new_password, user_id))
                db_connector.connect().commit()
                flash("Вы успешно сменили пароль", "susses")
                return redirect(url_for('users'))
    return render_template('change_password.html', errors=errors)


if __name__ == '__main__':
    print(app.config)
    app.run(host='0.0.0.0', port=8082, debug=True)
