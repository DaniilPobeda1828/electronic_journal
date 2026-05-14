import pytest
from datetime import date
from app import db, Group, User, Subject, Student

class TestTeacher:
    """Tests for teacher functionality"""
    
    def test_teacher_dashboard_access(self, client, auth_headers_teacher):
        """Check access to teacher dashboard"""
        response = client.get('/teacher')
        assert response.status_code == 200
    
    def test_teacher_grades_page(self, client, auth_headers_teacher):
        """Check grades page access"""
        with client.application.app_context():
            # Создаём тестовые данные
            teacher = User.query.filter_by(login='teacher_test_fixture').first()
            subject = Subject.query.filter_by(teacher_id=teacher.id).first()
            if not subject:
                subject = Subject(name='Test Subject for Grades', teacher_id=teacher.id)
                db.session.add(subject)
                db.session.commit()
            subject_id = subject.id
        
        response = client.get(f'/teacher/grades/{subject_id}')
        assert response.status_code == 200
    
    def test_add_grade(self, client, auth_headers_teacher):
        """Check adding a grade"""
        with client.application.app_context():
            # Создаём тестовые данные
            teacher = User.query.filter_by(login='teacher_test_fixture').first()
            subject = Subject.query.filter_by(teacher_id=teacher.id).first()
            if not subject:
                subject = Subject(name='Test Subject for Grade', teacher_id=teacher.id)
                db.session.add(subject)
                db.session.flush()
            
            group = Group.query.first()
            if not group:
                group = Group(name='Teacher Test Group')
                db.session.add(group)
                db.session.flush()
            
            student = Student.query.filter_by(group_id=group.id).first()
            if not student:
                student_user = User(login='teacher_test_student', full_name='Teacher Test Student', role='student')
                student_user.set_password('pass')
                db.session.add(student_user)
                db.session.flush()
                student = Student(full_name='Teacher Test Student', birth_date=date(2000, 1, 1), group_id=group.id, user_id=student_user.id)
                db.session.add(student)
                db.session.commit()
            
            student_id = student.id
            subject_id = subject.id
        
        response = client.post('/teacher/add_grade', data={
            'student_id': student_id,
            'subject_id': subject_id,
            'grade': 4,
            'work_type': 'practice',
            'date': date.today().isoformat()
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_teacher_schedule_access(self, client, auth_headers_teacher):
        """Check schedule access for teacher"""
        response = client.get('/schedule')
        assert response.status_code == 200