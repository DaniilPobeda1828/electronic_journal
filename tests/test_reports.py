import pytest
from app import db, Group, Student, Subject, Grade
from datetime import date

class TestReports:
    """Tests for reports functionality"""
    
    def test_debtors_report(self, client, auth_headers_admin):
        """Test debtors report"""
        response = client.get('/reports/debtors')
        assert response.status_code == 200
    
    def test_excellent_report(self, client, auth_headers_admin):
        """Test excellent students report"""
        response = client.get('/reports/excellent')
        assert response.status_code == 200
    
    def test_compare_groups_report(self, client, auth_headers_admin):
        """Test groups comparison report"""
        response = client.get('/reports/compare_groups')
        assert response.status_code == 200
    
    def test_charts_report(self, client, auth_headers_admin):
        """Test charts page"""
        response = client.get('/reports/charts')
        assert response.status_code == 200
    
    def test_export_excel(self, client, auth_headers_admin):
        """Test Excel export"""
        with client.application.app_context():
            # Создаём тестовую группу
            group = Group(name='Excel Export Group')
            db.session.add(group)
            db.session.commit()
            group_id = group.id
        
        response = client.get(f'/export/group/{group_id}')
        # Может быть 302 редирект или 200, проверяем что не 500
        assert response.status_code < 500