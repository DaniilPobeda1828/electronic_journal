from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import pandas as pd
from io import BytesIO
import os

# ==================== КОНФИГУРАЦИЯ ====================
class Config:
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///journal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'
    
    WORK_TYPES = ['лекция', 'практика', 'экзамен']
    GRADES = [2, 3, 4, 5]
    EXCELLENT_THRESHOLD = 4.75
    DEBTOR_THRESHOLD = 3.0

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== МОДЕЛИ БАЗЫ ДАННЫХ ====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    student = db.relationship('Student', backref='user', uselist=False)
    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    logs = db.relationship('ActionLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    students = db.relationship('Student', backref='group', lazy=True, cascade='all, delete-orphan')

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def get_average_grade(self):
        if not self.grades:
            return 0
        return sum(g.grade for g in self.grades) / len(self.grades)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    grades = db.relationship('Grade', backref='subject', lazy=True, cascade='all, delete-orphan')

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    work_type = db.Column(db.String(20), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'work_type', name='unique_student_subject_worktype'),
    )

class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    target = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    success = db.Column(db.Boolean, nullable=False)

# ==================== ДЕКОРАТОРЫ РОЛЕЙ ====================
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Доступ запрещён. Требуются права администратора.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_teacher() or current_user.is_admin()):
            flash('Доступ запрещён. Требуются права преподавателя.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ЗАГРУЗЧИК ПОЛЬЗОВАТЕЛЯ ====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def log_action(action, target=None):
    if current_user.is_authenticated:
        ip = request.remote_addr
        log = ActionLog(user_id=current_user.id, action=action, target=target, ip_address=ip)
        db.session.add(log)
        db.session.commit()

# ==================== МАРШРУТЫ ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        ip = request.remote_addr
        
        user = User.query.filter_by(login=login).first()
        
        if user and user.check_password(password):
            login_user(user)
            log_action('Вход в систему')
            attempt = LoginAttempt(login=login, ip_address=ip, success=True)
            db.session.add(attempt)
            db.session.commit()
            flash('Добро пожаловать!', 'success')
            return redirect(url_for('index'))
        else:
            attempt = LoginAttempt(login=login, ip_address=ip, success=False)
            db.session.add(attempt)
            db.session.commit()
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    log_action('Выход из системы')
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    recent_logs = ActionLog.query.order_by(ActionLog.timestamp.desc()).limit(10).all()
    
    if current_user.is_admin():
        groups_count = Group.query.count()
        students_count = Student.query.count()
        subjects_count = Subject.query.count()
        users_count = User.query.count()
        return render_template('index.html', 
                             groups_count=groups_count,
                             students_count=students_count,
                             subjects_count=subjects_count,
                             users_count=users_count,
                             recent_logs=recent_logs)
    elif current_user.is_teacher():
        subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
        return render_template('index.html', subjects=subjects, recent_logs=recent_logs)
    else:
        return render_template('index.html', recent_logs=recent_logs)

# ==================== АДМИН ПАНЕЛЬ ====================
@app.route('/admin')
@admin_required
def admin_dashboard():
    groups_count = Group.query.count()
    students_count = Student.query.count()
    subjects_count = Subject.query.count()
    users_count = User.query.count()
    return render_template('admin/dashboard.html',
                         groups_count=groups_count,
                         students_count=students_count,
                         subjects_count=subjects_count,
                         users_count=users_count)

@app.route('/admin/groups')
@admin_required
def admin_groups():
    groups = Group.query.all()
    return render_template('admin/groups.html', groups=groups)

@app.route('/admin/groups/add', methods=['POST'])
@admin_required
def add_group():
    name = request.form['name']
    if name:
        group = Group(name=name)
        db.session.add(group)
        db.session.commit()
        log_action(f'Добавлена группа {name}')
        flash('Группа добавлена', 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/groups/edit/<int:group_id>', methods=['POST'])
@admin_required
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)
    name = request.form['name']
    if name:
        group.name = name
        db.session.commit()
        log_action(f'Изменена группа на {name}')
        flash('Группа изменена', 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/groups/delete/<int:group_id>')
@admin_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    name = group.name
    db.session.delete(group)
    db.session.commit()
    log_action(f'Удалена группа {name}')
    flash('Группа удалена', 'success')
    return redirect(url_for('admin_groups'))

@app.route('/admin/students')
@admin_required
def admin_students():
    students = Student.query.all()
    groups = Group.query.all()
    return render_template('admin/students.html', students=students, groups=groups)

@app.route('/admin/students/add', methods=['POST'])
@admin_required
def add_student():
    full_name = request.form['full_name']
    birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
    group_id = request.form['group_id']
    
    login = f"student_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    user = User(login=login, password_hash=generate_password_hash(login), role='student', full_name=full_name)
    db.session.add(user)
    db.session.flush()
    
    student = Student(full_name=full_name, birth_date=birth_date, group_id=group_id, user_id=user.id)
    db.session.add(student)
    db.session.commit()
    
    log_action(f'Добавлен студент {full_name}')
    flash(f'Студент добавлен. Логин: {login}, пароль: {login}', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/students/edit/<int:student_id>', methods=['POST'])
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.full_name = request.form['full_name']
    student.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
    student.group_id = request.form['group_id']
    db.session.commit()
    log_action(f'Изменены данные студента {student.full_name}')
    flash('Данные студента обновлены', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/students/delete/<int:student_id>')
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.full_name
    if student.user:
        db.session.delete(student.user)
    db.session.delete(student)
    db.session.commit()
    log_action(f'Удалён студент {name}')
    flash('Студент удалён', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/subjects')
@admin_required
def admin_subjects():
    subjects = Subject.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('admin/subjects.html', subjects=subjects, teachers=teachers)

@app.route('/admin/subjects/add', methods=['POST'])
@admin_required
def add_subject():
    name = request.form['name']
    teacher_id = request.form['teacher_id']
    subject = Subject(name=name, teacher_id=teacher_id)
    db.session.add(subject)
    db.session.commit()
    log_action(f'Добавлен предмет {name}')
    flash('Предмет добавлен', 'success')
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/edit/<int:subject_id>', methods=['POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form['name']
    subject.teacher_id = request.form['teacher_id']
    db.session.commit()
    log_action(f'Изменён предмет {subject.name}')
    flash('Предмет изменён', 'success')
    return redirect(url_for('admin_subjects'))

@app.route('/admin/subjects/delete/<int:subject_id>')
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    name = subject.name
    db.session.delete(subject)
    db.session.commit()
    log_action(f'Удалён предмет {name}')
    flash('Предмет удалён', 'success')
    return redirect(url_for('admin_subjects'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@admin_required
def add_user():
    login = request.form['login']
    full_name = request.form['full_name']
    role = request.form['role']
    password = request.form['password']
    
    user = User(login=login, full_name=full_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_action(f'Добавлен пользователь {login}')
    flash('Пользователь добавлен', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.full_name = request.form['full_name']
    user.role = request.form['role']
    db.session.commit()
    log_action(f'Изменён пользователь {user.login}')
    flash('Пользователь изменён', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/reset/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form['new_password']
    user.set_password(new_password)
    db.session.commit()
    log_action(f'Сброшен пароль пользователя {user.login}')
    flash('Пароль изменён', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('Нельзя удалить администратора', 'danger')
    else:
        login = user.login
        db.session.delete(user)
        db.session.commit()
        log_action(f'Удалён пользователь {login}')
        flash('Пользователь удалён', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/logs')
@admin_required
def admin_logs():
    logs = ActionLog.query.order_by(ActionLog.timestamp.desc()).limit(200).all()
    login_attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(100).all()
    users = User.query.all()
    return render_template('admin/logs.html', logs=logs, login_attempts=login_attempts, users=users)

# ==================== ПРЕПОДАВАТЕЛЬ ====================
@app.route('/teacher')
@teacher_required
def teacher_dashboard():
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    total_students = 0
    total_grades = 0
    for subject in subjects:
        for grade in subject.grades:
            total_grades += 1
        for grade in subject.grades:
            if grade.student:
                total_students = len(set([g.student_id for g in subject.grades]))
    
    groups = set()
    for subject in subjects:
        for grade in subject.grades:
            if grade.student and grade.student.group:
                groups.add(grade.student.group)
    
    return render_template('teacher/dashboard.html', 
                         subjects=subjects, 
                         total_students=total_students,
                         total_grades=total_grades,
                         groups=list(groups))

@app.route('/teacher/grades/<int:subject_id>')
@teacher_required
def teacher_grades(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.teacher_id != current_user.id and not current_user.is_admin():
        flash('Нет доступа к этому предмету', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    groups = Group.query.all()
    selected_group = request.args.get('group_id')
    students = []
    if selected_group:
        students = Student.query.filter_by(group_id=selected_group).all()
    
    return render_template('teacher/grades.html', 
                         subject=subject, 
                         groups=groups, 
                         students=students, 
                         selected_group=selected_group,
                         now=date.today().isoformat())

@app.route('/teacher/add_grade', methods=['POST'])
@teacher_required
def add_grade():
    student_id = request.form['student_id']
    subject_id = request.form['subject_id']
    grade_value = int(request.form['grade'])
    work_type = request.form['work_type']
    grade_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    
    subject = Subject.query.get(subject_id)
    if subject.teacher_id != current_user.id and not current_user.is_admin():
        flash('Нет прав для выставления оценки', 'danger')
        return redirect(url_for('teacher_dashboard'))
    
    existing = Grade.query.filter_by(student_id=student_id, subject_id=subject_id, work_type=work_type).first()
    
    if existing:
        existing.grade = grade_value
        existing.date = grade_date
        flash('Оценка обновлена', 'success')
    else:
        grade = Grade(student_id=student_id, subject_id=subject_id, grade=grade_value, work_type=work_type, date=grade_date)
        db.session.add(grade)
        flash('Оценка выставлена', 'success')
    
    db.session.commit()
    student = Student.query.get(student_id)
    log_action(f'Выставлена оценка {grade_value} по предмету {subject.name} студенту {student.full_name}')
    
    return redirect(url_for('teacher_grades', subject_id=subject_id))

@app.route('/teacher/group_grades/<int:group_id>')
@teacher_required
def teacher_group_grades(group_id):
    group = Group.query.get_or_404(group_id)
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    students = Student.query.filter_by(group_id=group_id).all()
    
    grades_data = {}
    for student in students:
        grades_data[student.id] = {}
        for subject in subjects:
            grade_obj = Grade.query.filter_by(student_id=student.id, subject_id=subject.id).first()
            grades_data[student.id][subject.id] = grade_obj.grade if grade_obj else '-'
    
    # Статистика группы
    group_stats = {
        'avg_grade': 0,
        'excellent_count': 0,
        'debtor_count': 0,
        'passed_count': 0
    }
    
    grade_distribution = {5: 0, 4: 0, 3: 0, 2: 0}
    total_grades = 0
    
    for student in students:
        avg = student.get_average_grade()
        if avg >= 4.75:
            group_stats['excellent_count'] += 1
        elif avg < 3 and avg > 0:
            group_stats['debtor_count'] += 1
        elif avg > 0:
            group_stats['passed_count'] += 1
        
        for grade in student.grades:
            if grade.subject.teacher_id == current_user.id:
                grade_distribution[grade.grade] = grade_distribution.get(grade.grade, 0) + 1
                total_grades += 1
                group_stats['avg_grade'] += grade.grade
    
    if total_grades > 0:
        group_stats['avg_grade'] = group_stats['avg_grade'] / total_grades
    
    return render_template('teacher/group_grades.html', 
                         group=group, 
                         students=students, 
                         subjects=subjects, 
                         grades_data=grades_data,
                         group_stats=group_stats,
                         grade_distribution=grade_distribution,
                         total_grades=total_grades)

# ==================== СТУДЕНТ ====================
@app.route('/student/my_grades')
@login_required
def student_my_grades():
    if current_user.is_student():
        student = Student.query.filter_by(user_id=current_user.id).first()
    else:
        student_id = request.args.get('student_id')
        student = Student.query.get(student_id) if student_id else None
    
    if not student:
        flash('Студент не найден', 'danger')
        return redirect(url_for('index'))
    
    grades = Grade.query.filter_by(student_id=student.id).all()
    
    if grades:
        avg_grade = sum(g.grade for g in grades) / len(grades)
    else:
        avg_grade = 0
    
    return render_template('student/my_grades.html', student=student, grades=grades, avg_grade=avg_grade)

# ==================== ОТЧЁТЫ ====================
@app.route('/reports/debtors')
@login_required
def report_debtors():
    students_with_avg = []
    all_students = Student.query.all()
    
    for student in all_students:
        avg = student.get_average_grade()
        if avg < 3 and avg > 0:
            students_with_avg.append({
                'student': student,
                'avg_grade': avg,
                'group': student.group.name
            })
    
    return render_template('reports/debtors.html', students=students_with_avg)

@app.route('/reports/excellent')
@login_required
def report_excellent():
    excellent_students = []
    all_students = Student.query.all()
    
    for student in all_students:
        avg = student.get_average_grade()
        if avg >= 4.75:
            excellent_students.append({
                'student': student,
                'avg_grade': avg,
                'group': student.group.name
            })
    
    return render_template('reports/excellent.html', students=excellent_students)

@app.route('/reports/compare_groups')
@login_required
def report_compare_groups():
    groups = Group.query.all()
    group_stats = []
    
    for group in groups:
        students = Student.query.filter_by(group_id=group.id).all()
        all_grades = []
        for student in students:
            grades = Grade.query.filter_by(student_id=student.id).all()
            all_grades.extend([g.grade for g in grades])
        
        if all_grades:
            avg_grade = sum(all_grades) / len(all_grades)
        else:
            avg_grade = 0
        
        group_stats.append({
            'group': group,
            'student_count': len(students),
            'avg_grade': avg_grade
        })
    
    return render_template('reports/compare_groups.html', groups=group_stats)

@app.route('/reports/charts')
@login_required
def report_chart():
    groups = Group.query.all()
    selected_group_id = request.args.get('group_id', type=int)
    selected_group = None
    students = []
    subjects = []
    grade_distribution = {}
    subject_averages = {}
    total_grades_count = 0
    
    if selected_group_id:
        selected_group = Group.query.get(selected_group_id)
        if selected_group:
            students = Student.query.filter_by(group_id=selected_group_id).all()
            subjects = Subject.query.all()
            
            for student in students:
                for grade in student.grades:
                    total_grades_count += 1
                    grade_distribution[grade.grade] = grade_distribution.get(grade.grade, 0) + 1
            
            for subject in subjects:
                grades_sum = 0
                grades_count = 0
                for student in students:
                    for grade in student.grades:
                        if grade.subject_id == subject.id:
                            grades_sum += grade.grade
                            grades_count += 1
                if grades_count > 0:
                    subject_averages[subject.id] = grades_sum / grades_count
                else:
                    subject_averages[subject.id] = 0
    
    return render_template('reports/charts.html',
                         groups=groups,
                         selected_group_id=selected_group_id,
                         selected_group=selected_group,
                         students=students,
                         subjects=subjects,
                         grade_distribution=grade_distribution,
                         subject_averages=subject_averages,
                         total_grades_count=total_grades_count)

# ==================== ЭКСПОРТ В EXCEL (Модификация 1) ====================
@app.route('/export/group/<int:group_id>')
@login_required
def export_group_excel(group_id):
    import re
    
    group = Group.query.get_or_404(group_id)
    students = Student.query.filter_by(group_id=group_id).all()
    subjects = Subject.query.all()
    
    data = []
    for student in students:
        row = {
            'ФИО': student.full_name,
            'Дата рождения': student.birth_date.strftime('%d.%m.%Y'),
            'Группа': group.name,
            'Средний балл': f"{student.get_average_grade():.2f}"
        }
        for subject in subjects:
            grade = Grade.query.filter_by(student_id=student.id, subject_id=subject.id).first()
            row[subject.name] = grade.grade if grade else '-'
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Очищаем название листа от недопустимых символов
    invalid_chars = r'[\\/*?:\[\]]'
    sheet_name = re.sub(invalid_chars, '_', group.name)
    # Ограничиваем длину названия (Excel не любит длинные имена)
    sheet_name = sheet_name[:31]
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    output.seek(0)
    
    # Очищаем имя файла от недопустимых символов
    filename = re.sub(invalid_chars, '_', group.name)
    
    log_action(f'Экспорт успеваемости группы {group.name} в Excel')
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'успеваемость_{filename}.xlsx'
    )
# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Создание тестового администратора
        if User.query.count() == 0:
            admin = User(login='admin', role='admin', full_name='Администратор')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("=" * 50)
            print("Тестовый администратор создан:")
            print("Логин: admin")
            print("Пароль: admin123")
            print("=" * 50)
    
    app.run(debug=True, host='127.0.0.1', port=5000)