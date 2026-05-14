import sys
import os
import pytest
from datetime import date, datetime

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User, Group, Student, Subject, Grade, Schedule, ActionLog, LoginAttempt

@pytest.fixture
def client():
    """Тестовый клиент Flask"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def init_database(client):
    """Инициализация тестовой БД с данными"""
    with app.app_context():
        # Удаляем все существующие данные
        db.session.query(LoginAttempt).delete()
        db.session.query(ActionLog).delete()
        db.session.query(Grade).delete()
        db.session.query(Schedule).delete()
        db.session.query(Student).delete()
        db.session.query(Subject).delete()
        db.session.query(Group).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Создаём администратора
        admin = User(
            login='admin',
            full_name='Test Admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        
        # Создаём преподавателя
        teacher = User(
            login='teacher',
            full_name='Test Teacher',
            role='teacher'
        )
        teacher.set_password('teacher123')
        db.session.add(teacher)
        db.session.flush()
        
        # Создаём группу
        group = Group(name='TEST-GROUP-01')
        db.session.add(group)
        db.session.flush()
        
        # Создаём студента
        student_user = User(
            login='student_test',
            full_name='Test Student',
            role='student'
        )
        student_user.set_password('student123')
        db.session.add(student_user)
        db.session.flush()
        
        student = Student(
            full_name='Test Student',
            birth_date=date(2000, 1, 1),
            group_id=group.id,
            user_id=student_user.id
        )
        db.session.add(student)
        db.session.flush()
        
        # Создаём предмет
        subject = Subject(
            name='Test Subject',
            teacher_id=teacher.id
        )
        db.session.add(subject)
        db.session.flush()
        
        # Создаём оценку
        grade = Grade(
            student_id=student.id,
            subject_id=subject.id,
            grade=5,
            work_type='exam',
            date=date.today()
        )
        db.session.add(grade)
        
        db.session.commit()
        
        # Возвращаем ID объектов (не сами объекты, чтобы избежать detached)
        return {
            'admin_id': admin.id,
            'teacher_id': teacher.id,
            'student_user_id': student_user.id,
            'student_id': student.id,
            'group_id': group.id,
            'subject_id': subject.id,
            'grade_id': grade.id
        }
    
@pytest.fixture
def auth_headers_admin(client):
    """Авторизация администратора"""
    with client.application.app_context():
        # Создаём админа если нет
        admin = User.query.filter_by(login='admin_test_fixture').first()
        if not admin:
            admin = User(
                login='admin_test_fixture',
                full_name='Test Admin Fixture',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    client.post('/login', data={
        'login': 'admin_test_fixture',
        'password': 'admin123'
    })
    return client

@pytest.fixture
def auth_headers_teacher(client):
    """Авторизация преподавателя"""
    with client.application.app_context():
        # Создаём преподавателя если нет
        teacher = User.query.filter_by(login='teacher_test_fixture').first()
        if not teacher:
            teacher = User(
                login='teacher_test_fixture',
                full_name='Test Teacher Fixture',
                role='teacher'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            db.session.commit()
    
    client.post('/login', data={
        'login': 'teacher_test_fixture',
        'password': 'teacher123'
    })
    return client

@pytest.fixture
def auth_headers_student(client):
    """Авторизация студента"""
    with client.application.app_context():
        # Создаём группу
        group = Group.query.filter_by(name='Student Test Group').first()
        if not group:
            group = Group(name='Student Test Group')
            db.session.add(group)
            db.session.flush()
        
        # Создаём студента если нет
        student = Student.query.filter_by(full_name='Test Student Fixture').first()
        if not student:
            student_user = User(
                login='student_test_fixture',
                full_name='Test Student Fixture',
                role='student'
            )
            student_user.set_password('student123')
            db.session.add(student_user)
            db.session.flush()
            
            student = Student(
                full_name='Test Student Fixture',
                birth_date=date(2000, 1, 1),
                group_id=group.id,
                user_id=student_user.id
            )
            db.session.add(student)
            db.session.commit()
    
    client.post('/login', data={
        'login': 'student_test_fixture',
        'password': 'student123'
    })
    return client