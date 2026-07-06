"""
API Tests for Employee Endpoints

These tests verify the full request-response cycle.
They use DRF's APIClient with a real test database.

Architecture Rule: API tests test the complete HTTP flow.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from uuid import uuid4

from apps.departments.infrastructure.models import DepartmentModel
from apps.employees.infrastructure.models import EmployeeModel


class TestEmployeeAPI(TestCase):
    """Test Employee API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        
        # Create a department
        self.dept = DepartmentModel.objects.create(
            code='ENG',
            name='Engineering',
            is_active=True,
        )
        
        # Create an employee
        self.employee = EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-001',
            first_name='Abebe',
            last_name='Kebede',
            email='abebe@company.com',
            department=self.dept,
            job_title='Software Engineer',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
    
    def test_list_employees_returns_paginated_response(self):
        """Test that GET /api/employees/ returns paginated response."""
        response = self.client.get('/api/employees/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(response.data['count'], 1)
    
    def test_list_employees_with_search_filter(self):
        """Test that search filter works."""
        # Create another employee
        EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-002',
            first_name='Beyene',
            last_name='Tesfaye',
            email='beyene@company.com',
            department=self.dept,
            job_title='Software Engineer',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
        
        response = self.client.get('/api/employees/?search=Abebe')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Abebe')
    
    def test_list_employees_with_department_filter(self):
        """Test that department filter works."""
        # Create another department
        dept2 = DepartmentModel.objects.create(
            code='HR',
            name='Human Resources',
            is_active=True,
        )
        
        # Create employee in HR
        EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-002',
            first_name='Beyene',
            last_name='Tesfaye',
            email='beyene@company.com',
            department=dept2,
            job_title='HR Manager',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
        
        response = self.client.get('/api/employees/?department=ENG')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['employee_number'], 'EMP-001')
    
    def test_retrieve_employee_returns_nested_department(self):
        """Test that GET /api/employees/{id}/ returns nested department."""
        response = self.client.get(f'/api/employees/{self.employee.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_number'], 'EMP-001')
        self.assertIn('department', response.data)
        self.assertEqual(response.data['department']['code'], 'ENG')
        self.assertEqual(response.data['department']['name'], 'Engineering')
    
    def test_retrieve_nonexistent_employee_returns_404(self):
        """Test that retrieving nonexistent employee returns 404."""
        response = self.client.get(f'/api/employees/{uuid4()}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_employee_succeeds(self):
        """Test that POST /api/employees/ creates an employee."""
        data = {
            'first_name': 'Beyene',
            'last_name': 'Tesfaye',
            'email': 'beyene@company.com',
            'department_id': str(self.dept.id),
            'job_title': 'Software Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': '2023-01-15',
        }
        
        response = self.client.post('/api/employees/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Beyene')
        self.assertEqual(response.data['employee_number'], 'EMP-002')
        self.assertEqual(response.data['email'], 'beyene@company.com')
    
    def test_create_employee_with_missing_field_returns_400(self):
        """Test that missing required field returns 400."""
        data = {
            'first_name': 'Beyene',
            'last_name': 'Tesfaye',
            # Missing email
            'department_id': str(self.dept.id),
            'job_title': 'Software Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': '2023-01-15',
        }
        
        response = self.client.post('/api/employees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_employee_with_duplicate_email_returns_400(self):
        """Test that duplicate email returns 400."""
        data = {
            'first_name': 'Beyene',
            'last_name': 'Tesfaye',
            'email': 'abebe@company.com',  # Duplicate email
            'department_id': str(self.dept.id),
            'job_title': 'Software Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': '2023-01-15',
        }
        
        response = self.client.post('/api/employees/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_employee_succeeds(self):
        """Test that PUT /api/employees/{id}/ updates an employee."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@company.com',
            'department_id': str(self.dept.id),
            'job_title': 'Senior Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': '2023-01-15',
        }
        
        response = self.client.put(f'/api/employees/{self.employee.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['email'], 'updated@company.com')
    
    def test_delete_employee_sets_is_active_false(self):
        """Test that DELETE /api/employees/{id}/ soft deletes."""
        response = self.client.delete(f'/api/employees/{self.employee.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify employee is still in database but inactive
        employee = EmployeeModel.objects.get(id=self.employee.id)
        self.assertFalse(employee.is_active)
    
    def test_bulk_delete_returns_structured_response(self):
        """Test that bulk delete returns structured response."""
        # Create another employee
        emp2 = EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-002',
            first_name='Beyene',
            last_name='Tesfaye',
            email='beyene@company.com',
            department=self.dept,
            job_title='Software Engineer',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
        
        data = {
            'ids': [str(self.employee.id), str(emp2.id), str(uuid4())]
        }
        
        response = self.client.post('/api/employees/bulk-delete/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deactivated', response.data)
        self.assertIn('already_inactive', response.data)
        self.assertIn('not_found', response.data)
        self.assertEqual(response.data['deactivated'], 2)
        self.assertEqual(response.data['not_found'], 1)
    
    def test_pagination_works(self):
        """Test that pagination is applied."""
        # Create multiple employees
        for i in range(25):
            EmployeeModel.objects.create(
                id=uuid4(),
                employee_number=f'EMP-{i+2:03d}',
                first_name=f'Employee{i}',
                last_name=f'Test{i}',
                email=f'employee{i}@company.com',
                department=self.dept,
                job_title='Engineer',
                employment_type='FULL_TIME',
                hire_date=date(2023, 1, 15),
                is_active=True,
            )
        
        response = self.client.get('/api/employees/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
        self.assertIsNotNone(response.data['next'])