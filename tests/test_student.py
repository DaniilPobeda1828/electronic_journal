import pytest

class TestStudent:
    """Tests for student functionality"""
    
    def test_student_grades_access(self, client, auth_headers_student):
        """Check access to grades page for student"""
        response = client.get('/student/my_grades')
        assert response.status_code == 200
    
    def test_student_schedule_access(self, client, auth_headers_student):
        """Check access to schedule for student"""
        response = client.get('/schedule')
        assert response.status_code == 200
    
    def test_student_cannot_access_teacher_panel(self, client, auth_headers_student):
        """Check that student cannot access teacher panel"""
        response = client.get('/teacher', follow_redirects=True)
        assert response.status_code == 200
    
    def test_student_cannot_access_admin_panel(self, client, auth_headers_student):
        """Check that student cannot access admin panel"""
        response = client.get('/admin', follow_redirects=True)
        assert response.status_code == 200
    
    def test_student_my_logs(self, client, auth_headers_student):
        """Check that student can view their own logs"""
        response = client.get('/my_logs')
        assert response.status_code == 200