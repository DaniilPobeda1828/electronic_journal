import pytest
from app import db, Group, User, Subject, Schedule

class TestSchedule:
    """Tests for schedule functionality"""
    
    def test_add_schedule_item(self, client, auth_headers_admin):
        """Test adding schedule item"""
        with client.application.app_context():
            # Создаём тестовую группу
            group = Group(name='Schedule Test Group')
            db.session.add(group)
            
            # Создаём преподавателя
            teacher = User(login='schedule_teacher_test', full_name='Schedule Teacher', role='teacher')
            teacher.set_password('pass')
            db.session.add(teacher)
            db.session.flush()
            
            # Создаём предмет
            subject = Subject(name='Schedule Test Subject', teacher_id=teacher.id)
            db.session.add(subject)
            db.session.commit()
            
            group_id = group.id
            subject_id = subject.id
        
        response = client.post('/admin/schedule/add', data={
            'group_id': group_id,
            'subject_id': subject_id,
            'classroom': '101',
            'day_of_week': 2,
            'start_time': '10:00',
            'end_time': '11:30'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_view_schedule(self, client, auth_headers_admin):
        """Test viewing schedule"""
        response = client.get('/schedule')
        assert response.status_code == 200