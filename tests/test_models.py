import pytest
from app import db, User, Group, Student, Subject, Grade, Schedule
from datetime import date

class TestModels:
    """Tests for data models"""
    
    def test_create_user(self, client):
        """Test user creation"""
        with client.application.app_context():
            user = User(
                login='test_user_model',
                full_name='Test User Model',
                role='student'
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            
            saved_user = db.session.get(User, user.id)
            assert saved_user is not None
            assert saved_user.full_name == 'Test User Model'
            assert saved_user.role == 'student'
            assert saved_user.check_password('test123') is True
    
    def test_create_group(self, client):
        """Test group creation"""
        with client.application.app_context():
            group = Group(name='TEST-GROUP-MODEL')
            db.session.add(group)
            db.session.commit()
            
            saved_group = db.session.get(Group, group.id)
            assert saved_group is not None
            assert saved_group.name == 'TEST-GROUP-MODEL'
    
    def test_user_is_admin_method(self, client):
        """Test is_admin method"""
        with client.application.app_context():
            # Исправлено: устанавливаем пароли для всех пользователей
            admin = User(login='admin_test_model', full_name='Admin', role='admin')
            admin.set_password('admin_pass')
            
            teacher = User(login='teacher_test_model', full_name='Teacher', role='teacher')
            teacher.set_password('teacher_pass')
            
            student = User(login='student_test_model', full_name='Student', role='student')
            student.set_password('student_pass')
    
            db.session.add_all([admin, teacher, student])
            db.session.commit()
            
            # Проверяем методы
            assert admin.is_admin() is True
            assert teacher.is_admin() is False
            assert student.is_admin() is False
    
    def test_create_schedule(self, client):
        """Test schedule creation"""
        with client.application.app_context():
            # Создаём группу
            group = Group(name='Schedule Group')
            db.session.add(group)
            db.session.flush()
            
            # Создаём преподавателя
            teacher = User(login='schedule_teacher', full_name='Schedule Teacher', role='teacher')
            teacher.set_password('pass')
            db.session.add(teacher)
            db.session.flush()
            
            # Создаём предмет
            subject = Subject(name='Schedule Subject', teacher_id=teacher.id)
            db.session.add(subject)
            db.session.flush()
            
            # Создаём расписание
            schedule = Schedule(
                group_id=group.id,
                subject_id=subject.id,
                classroom='201',
                day_of_week=1,
                start_time='09:00',
                end_time='10:30'
            )
            db.session.add(schedule)
            db.session.commit()
            
            saved_schedule = db.session.get(Schedule, schedule.id)
            assert saved_schedule is not None
            assert saved_schedule.classroom == '201'