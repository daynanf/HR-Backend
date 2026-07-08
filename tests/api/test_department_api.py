"""
API Tests for Department Endpoints

These tests verify the full request-response cycle for department operations.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from uuid import uuid4

from apps.departments.infrastructure.models import DepartmentModel
from apps.employees.infrastructure.models import EmployeeModel
from datetime import date


class TestDepartmentAPI(TestCase):
    """Test Department API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create a department
        self.department = DepartmentModel.objects.create(
            code='ENG',
            name='Engineering',
            description='Software Engineering Department',
            is_active=True,
        )
        
        # Create another department
        self.dept2 = DepartmentModel.objects.create(
            code='HR',
            name='Human Resources',
            description='HR Department',
            is_active=True,
        )
    
    def test_list_departments_returns_all_departments(self):
        """Test that GET /api/departments/ returns all departments."""
        response = self.client.get('/api/departments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['code'], 'ENG')
        self.assertEqual(response.data[1]['code'], 'HR')
    
    def test_list_departments_returns_correct_data_structure(self):
        """Test that department list returns the correct data structure."""
        response = self.client.get('/api/departments/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dept = response.data[0]
        self.assertIn('id', dept)
        self.assertIn('code', dept)
        self.assertIn('name', dept)
        self.assertIn('description', dept)
        self.assertIn('is_active', dept)
    
    def test_retrieve_department_succeeds(self):
        """Test that GET /api/departments/{id}/ returns a department."""
        response = self.client.get(f'/api/departments/{self.department.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'ENG')
        self.assertEqual(response.data['name'], 'Engineering')
        self.assertEqual(response.data['description'], 'Software Engineering Department')
        self.assertTrue(response.data['is_active'])
    
    def test_retrieve_nonexistent_department_returns_404(self):
        """Test that retrieving nonexistent department returns 404."""
        response = self.client.get(f'/api/departments/{uuid4()}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_department_succeeds(self):
        """Test that POST /api/departments/ creates a department."""
        data = {
            'code': 'FIN',
            'name': 'Finance',
            'description': 'Finance Department',
        }
        
        response = self.client.post('/api/departments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'FIN')
        self.assertEqual(response.data['name'], 'Finance')
        self.assertEqual(response.data['description'], 'Finance Department')
        self.assertTrue(response.data['is_active'])
    
    def test_create_department_without_description_succeeds(self):
        """Test that creating a department without description works."""
        data = {
            'code': 'FIN',
            'name': 'Finance',
        }
        
        response = self.client.post('/api/departments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'FIN')
        self.assertIsNone(response.data['description'])
    
    def test_create_duplicate_department_code_returns_400(self):
        """Test that duplicate department code returns 400."""
        data = {
            'code': 'ENG',  # Duplicate code
            'name': 'Engineering 2',
            'description': 'Another Engineering Department',
        }
        
        response = self.client.post('/api/departments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_department_with_empty_code_returns_400(self):
        """Test that empty code returns 400."""
        data = {
            'code': '',
            'name': 'Invalid Department',
        }
        
        response = self.client.post('/api/departments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_department_with_empty_name_returns_400(self):
        """Test that empty name returns 400."""
        data = {
            'code': 'INV',
            'name': '',
        }
        
        response = self.client.post('/api/departments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_department_with_non_alphanumeric_code_returns_400(self):
        """Test that non-alphanumeric code returns 400."""
        data = {
            'code': 'ENG-123',  # Contains dash
            'name': 'Engineering',
        }
        
        response = self.client.post('/api/departments/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_department_succeeds(self):
        """Test that PUT /api/departments/{id}/ updates a department."""
        data = {
            'code': 'SOFT',
            'name': 'Software Engineering',
            'description': 'Updated Software Engineering Department',
        }
        
        response = self.client.put(f'/api/departments/{self.department.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'SOFT')
        self.assertEqual(response.data['name'], 'Software Engineering')
        self.assertEqual(response.data['description'], 'Updated Software Engineering Department')
    
    def test_update_department_partial_succeeds(self):
        """Test that partial update of a department works."""
        data = {
            'name': 'Software Engineering',
        }
        
        response = self.client.patch(f'/api/departments/{self.department.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'ENG')  # Unchanged
        self.assertEqual(response.data['name'], 'Software Engineering')
        self.assertEqual(response.data['description'], 'Software Engineering Department')  # Unchanged
    
    def test_update_department_with_duplicate_code_returns_400(self):
        """Test that updating to a duplicate code returns 400."""
        data = {
            'code': 'HR',  # Already exists
            'name': 'Engineering',
        }
        
        response = self.client.put(f'/api/departments/{self.department.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_nonexistent_department_returns_404(self):
        """Test that updating nonexistent department returns 404."""
        data = {
            'code': 'NEW',
            'name': 'New Department',
        }
        
        response = self.client.put(f'/api/departments/{uuid4()}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_deactivate_department_with_no_employees_succeeds(self):
        """Test that deactivating a department with no employees works."""
        response = self.client.post(f'/api/departments/{self.dept2.id}/deactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify department is deactivated
        dept = DepartmentModel.objects.get(id=self.dept2.id)
        self.assertFalse(dept.is_active)
    
    def test_deactivate_department_with_active_employees_returns_400(self):
        """Test that deactivating a department with active employees returns 400."""
        # Create an employee in this department
        EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-001',
            first_name='Abebe',
            last_name='Kebede',
            email='abebe@company.com',
            department=self.department,
            job_title='Software Engineer',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
        
        response = self.client.post(f'/api/departments/{self.department.id}/deactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_deactivate_already_inactive_department(self):
        """Test that deactivating an already inactive department works."""
        # Deactivate first
        self.client.post(f'/api/departments/{self.dept2.id}/deactivate/')
        
        # Try to deactivate again
        response = self.client.post(f'/api/departments/{self.dept2.id}/deactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # It should work because it just sets is_active=False again
    
    def test_deactivate_nonexistent_department_returns_404(self):
        """Test that deactivating nonexistent department returns 404."""
        response = self.client.post(f'/api/departments/{uuid4()}/deactivate/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_department_response_includes_is_active(self):
        """Test that department response includes is_active field."""
        response = self.client.get(f'/api/departments/{self.department.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_active', response.data)
        self.assertTrue(response.data['is_active'])
        
        # Deactivate and check again
        self.client.post(f'/api/departments/{self.department.id}/deactivate/')
        response = self.client.get(f'/api/departments/{self.department.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])