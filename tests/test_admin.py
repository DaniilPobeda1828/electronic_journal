import pytest
from app import db, Group, User

class TestAdmin:
    """Tests for administrator functionality"""
    
    def test_admin_dashboard_access(self, client):
        """Check access to admin dashboard"""
        # Создаём админа для теста
        with client.application.app_context():
            admin = User(
                login='test_admin',
                full_name='Test Admin',
                role='admin'
            )
            admin.set_password('test123')
            db.session.add(admin)
            db.session.commit()
            admin_id = admin.id
        
        # Логинимся
        client.post('/login', data={
            'login': 'test_admin',
            'password': 'test123'
        })
        
        response = client.get('/admin')
        assert response.status_code == 200
    
    def test_add_group(self, client):
        """Check adding a group"""
        # Создаём админа
        with client.application.app_context():
            admin = User(
                login='test_admin2',
                full_name='Test Admin 2',
                role='admin'
            )
            admin.set_password('test123')
            db.session.add(admin)
            db.session.commit()
        
        client.post('/login', data={
            'login': 'test_admin2',
            'password': 'test123'
        })
        
        response = client.post('/admin/groups/add', data={
            'name': 'NEW-GROUP-TEST'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_admin_logs_access(self, client):
        """Check access to logs"""
        with client.application.app_context():
            admin = User(
                login='test_admin3',
                full_name='Test Admin 3',
                role='admin'
            )
            admin.set_password('test123')
            db.session.add(admin)
            db.session.commit()
        
        client.post('/login', data={
            'login': 'test_admin3',
            'password': 'test123'
        })
        
        response = client.get('/admin/logs')
        assert response.status_code == 200