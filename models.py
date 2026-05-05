from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ==================== ПОЛЬЗОВАТЕЛИ ====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Связи
    student = db.relationship('Student', backref='user', uselist=False)
    subjects = db.relationship('Subject', backref='teacher', lazy=True)
    logs = db.relationship('ActionLog', backref='user', lazy=True)
    
    def set_password(self, password):
        """Хэширование пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def __repr__(self):
        return f'<User {self.login} ({self.role})>'

# ==================== ГРУППЫ ====================
class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Связи
    students = db.relationship('Student', backref='group', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Group {self.name}>'

# ==================== СТУДЕНТЫ ====================
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    # Связи
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def get_average_grade(self):
        """Получение среднего балла студента"""
        if not self.grades:
            return 0
        return sum(g.grade for g in self.grades) / len(self.grades)
    
    def __repr__(self):
        return f'<Student {self.full_name}>'

# ==================== ПРЕДМЕТЫ ====================
class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Связи
    grades = db.relationship('Grade', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.name}>'

# ==================== ОЦЕНКИ ====================
class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    work_type = db.Column(db.String(20), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'work_type', 
                           name='unique_student_subject_worktype'),
    )
    
    def __repr__(self):
        return f'<Grade {self.grade} for student {self.student_id}>'

# ==================== ЛОГИ ДЕЙСТВИЙ ====================
class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    target = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    def __repr__(self):
        return f'<ActionLog {self.action} by {self.user_id}>'

# ==================== ПОПЫТКИ ВХОДА ====================
class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    success = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f'<LoginAttempt {self.login} - {"Success" if self.success else "Failed"}>'