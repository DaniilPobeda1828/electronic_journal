from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Декоратор: доступ только для администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, авторизуйтесь', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_admin():
            flash('Доступ запрещён. Требуются права администратора.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Декоратор: доступ для преподавателя и администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, авторизуйтесь', 'warning')
            return redirect(url_for('login'))
        if not (current_user.is_teacher() or current_user.is_admin()):
            flash('Доступ запрещён. Требуются права преподавателя.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Декоратор: доступ только для студента"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, авторизуйтесь', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_student():
            flash('Доступ запрещён.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_or_admin_required(f):
    """Декоратор: доступ для преподавателя или администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, авторизуйтесь', 'warning')
            return redirect(url_for('login'))
        if not (current_user.is_teacher() or current_user.is_admin()):
            flash('Доступ запрещён.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function