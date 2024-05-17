import psycopg
from psycopg.rows import namedtuple_row
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db_connector
from auth import check_for_privelege

bp = Blueprint('users', __name__, url_prefix='/users')


def get_roles():
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        cursor.execute("SELECT * FROM roles")
        return cursor.fetchall()


@bp.route('/')
def index():
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        cursor.execute("SELECT users.*, roles.name AS role FROM users LEFT JOIN roles ON users.role_id = roles.id")
        users = cursor.fetchall()
        return render_template('users/index.html', users=users)


@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@check_for_privelege('delete')
def delete(user_id):
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        try:
            query = ("DELETE FROM users WHERE id = %s")
            cursor.execute(query, (user_id,))
            db_connector.connect().commit()
        except psycopg.Error as ex:
            db_connector.connect().rollback()

    flash('Учетная запись успешно удалена', 'success')
    return redirect(url_for('users.index'))


@bp.route('/new', methods=['POST', 'GET'])
@login_required
@check_for_privelege('create')
def new():
    user_data = {}
    if request.method == 'POST':
        fields = ('login', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form[field] or None for field in fields}
        with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
            try:
                query = (
                    "INSERT INTO users (login, password_hash, first_name, middle_name, last_name, role_id) VALUES "
                    "(%(login)s, CAST(SHA256(%(password)s) AS VARCHAR), %(first_name)s, %(middle_name)s, %(last_name)s, %(role_id)s)"
                )
                cursor.execute(query, user_data)
                db_connector.connect().commit()
                flash('Учетная запись успешно создана', 'success')
                return redirect(url_for('users.index'))
            except psycopg.Error:
                flash('Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены', 'danger')

    return render_template('users/new.html', user_data=user_data, roles=get_roles())


@bp.route('/<int:user_id>/view')
@check_for_privelege('read')
def view(user_id):
    user_data = {}
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        query = ("SELECT * FROM users WHERE id = %s")
        cursor.execute(query, [user_id])
        user_data = cursor.fetchone()
        if user_data is None:
            flash('Пользователя нет в базе данных', 'danger')
            return redirect(url_for('users.index'))
        query = "SELECT name FROM roles WHERE id = %s"
        cursor.execute(query, [user_data.role_id])
        user_role = cursor.fetchone()
        return render_template('users/view.html', user_data=user_data, user_role=user_role.name)


@bp.route('/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
@check_for_privelege('update')
def edit(user_id):
    with db_connector.connect().cursor(row_factory=namedtuple_row) as cursor:
        query = ("SELECT first_name, middle_name, last_name, role_id "
                 "FROM users WHERE id = %s")
        cursor.execute(query, [user_id])
        user_data = cursor.fetchone()
        if user_data is None:
            flash('Пользователя нет в базе данных', 'danger')
            return redirect(url_for('users'))

        if request.method == 'POST':
            fields = ['first_name', 'middle_name', 'last_name', 'role_id']
            if not current_user.can('assign_role'):
                fields.remove('role_id')
            user_data = {field: request.form[field] or None for field in fields}
            user_data['id'] = user_id
            try:
                field_assignments = ', '.join([f"{field} = %({field})s" for field in fields])
                query = (f"UPDATE users SET {field_assignments} "
                         "WHERE id = %(id)s")
                cursor.execute(query, user_data)
                db_connector.connect().commit()
                flash('Учетная запись успешно изменена', 'success')
                return redirect(url_for('users.index'))
            except psycopg.Error as error:
                flash(f'Произошла ошибка при изменении записи: {error}', 'danger')
    return render_template('users/edit.html', user_data=user_data, roles=get_roles())
