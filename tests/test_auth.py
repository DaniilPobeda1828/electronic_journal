import pytest
from app import db, User

class TestAuth:
    """Tests for authentication"""
    
    def test_login_page(self, client):
        """Check login page loading"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'Login' in response.data
    
    def test_valid_admin_login(self, client):
        """Check login with valid credentials (admin)"""
        # Создаём админа
        with client.application.app_context():
            admin = User(
                login='admin_test',
                full_name='Test Admin',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        response = client.post('/login', data={
            'login': 'admin_test',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_invalid_login(self, client):
        """Check login with invalid credentials"""
        response = client.post('/login', data={
            'login': 'wrong_user',
            'password': 'wrong_pass'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_logout(self, client):
        """Check logout functionality"""
        with client.application.app_context():
            admin = User(
                login='logout_test',
                full_name='Logout Test',
                role='admin'
            )
            admin.set_password('test123')
            db.session.add(admin)
            db.session.commit()
        
        client.post('/login', data={
            'login': 'logout_test',
            'password': 'test123'
        })
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200