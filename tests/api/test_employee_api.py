"""
API Tests for Employee Endpoints

These tests verify the full request-response cycle for employee operations.
They use DRF's APIClient with a real test database.

Architecture Rule: API tests test the complete HTTP flow.
"""

from django.test import TestCase
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
    
    def test_list_employees_returns_correct_data_structure(self):
        """Test that employee list returns the correct data structure."""
        response = self.client.get('/api/employees/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data['results'][0]
        self.assertIn('id', result)
        self.assertIn('employee_number', result)
        self.assertIn('first_name', result)
        self.assertIn('last_name', result)
        self.assertIn('email', result)
        self.assertIn('department', result)
        self.assertIn('job_title', result)
        self.assertIn('employment_type', result)
        self.assertIn('hire_date', result)
        self.assertIn('is_active', result)
    
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
    
    def test_list_employees_with_search_filter_case_insensitive(self):
        """Test that search filter is case insensitive."""
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
        
        response = self.client.get('/api/employees/?search=abebe')
        
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
    
    def test_list_employees_with_combined_filters(self):
        """Test that combined search and department filters work."""
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
            first_name='Abebe',
            last_name='Tesfaye',
            email='abebe2@company.com',
            department=dept2,
            job_title='HR Manager',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
        
        # Search for Abebe in ENG department
        response = self.client.get('/api/employees/?search=Abebe&department=ENG')
        
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
        
        # FIX: Add format='json' to send JSON data
        response = self.client.post('/api/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Beyene')
        self.assertEqual(response.data['employee_number'], 'EMP-002')
        self.assertEqual(response.data['email'], 'beyene@company.com')
        self.assertIn('department', response.data)
        self.assertEqual(response.data['department']['code'], 'ENG')
    
    def test_create_employee_auto_generates_employee_number(self):
        """Test that employee number is auto-generated if not provided."""
        data = {
            'first_name': 'Beyene',
            'last_name': 'Tesfaye',
            'email': 'beyene@company.com',
            'department_id': str(self.dept.id),
            'job_title': 'Software Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': '2023-01-15',
            # No employee_number provided
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/employees/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['employee_number'], 'EMP-002')
    
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
        
        # FIX: Add format='json'
        response = self.client.post('/api/employees/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_employee_with_duplicate_email_returns_400(self):
        """Test that duplicate email returns 400 with clear error message."""
        data = {
            'first_name': 'Beyene',
            'last_name': 'Tesfaye',
            'email': 'abebe@company.com',  # Duplicate email
            'department_id': str(self.dept.id),
            'job_title': 'Software Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': '2023-01-15',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/employees/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_employee_with_invalid_employment_type_returns_400(self):
        """Test that invalid employment type returns 400."""
        data = {
            'first_name': 'Beyene',
            'last_name': 'Tesfaye',
            'email': 'beyene@company.com',
            'department_id': str(self.dept.id),
            'job_title': 'Software Engineer',
            'employment_type': 'INVALID_TYPE',
            'hire_date': '2023-01-15',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/employees/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
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
        
        # FIX: Add format='json'
        response = self.client.put(f'/api/employees/{self.employee.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['email'], 'updated@company.com')
        self.assertEqual(response.data['job_title'], 'Senior Engineer')
    
    def test_partial_update_employee_succeeds(self):
        """Test that PATCH /api/employees/{id}/ partially updates an employee."""
        data = {
            'first_name': 'Partially',
            'job_title': 'Lead Engineer',
        }
        
        # FIX: Add format='json'
        response = self.client.patch(f'/api/employees/{self.employee.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Partially')
        self.assertEqual(response.data['job_title'], 'Lead Engineer')
        self.assertEqual(response.data['email'], 'abebe@company.com')  # Unchanged
    
    def test_update_employee_with_duplicate_email_returns_400(self):
        """Test that updating to a duplicate email returns 400."""
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
        
        # Try to update first employee with second employee's email
        data = {'email': 'beyene@company.com'}
        # FIX: Add format='json'
        response = self.client.patch(f'/api/employees/{self.employee.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_delete_employee_sets_is_active_false(self):
        """Test that DELETE /api/employees/{id}/ soft deletes."""
        response = self.client.delete(f'/api/employees/{self.employee.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify employee is still in database but inactive
        employee = EmployeeModel.objects.get(id=self.employee.id)
        self.assertFalse(employee.is_active)
    
    def test_delete_employee_does_not_hard_delete(self):
        """Test that employee record still exists after delete."""
        response = self.client.delete(f'/api/employees/{self.employee.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify employee still exists in database
        employee_count = EmployeeModel.objects.filter(id=self.employee.id).count()
        self.assertEqual(employee_count, 1)
    
    def test_delete_nonexistent_employee_returns_404(self):
        """Test that deleting nonexistent employee returns 404."""
        response = self.client.delete(f'/api/employees/{uuid4()}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
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
        
        # FIX: Add format='json'
        response = self.client.post('/api/employees/bulk-delete/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deactivated', response.data)
        self.assertIn('already_inactive', response.data)
        self.assertIn('not_found', response.data)
        self.assertEqual(response.data['deactivated'], 2)
        self.assertEqual(response.data['not_found'], 1)
    
    def test_bulk_delete_with_empty_ids_returns_400(self):
        """Test that bulk delete with empty ids returns 400."""
        data = {'ids': []}
        # FIX: Add format='json'
        response = self.client.post('/api/employees/bulk-delete/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_delete_with_already_inactive_employees(self):
        """Test that bulk delete handles already inactive employees correctly."""
        # Create an inactive employee
        inactive = EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-002',
            first_name='Inactive',
            last_name='User',
            email='inactive@company.com',
            department=self.dept,
            job_title='Software Engineer',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=False,
        )
        
        data = {'ids': [str(self.employee.id), str(inactive.id)]}
        # FIX: Add format='json'
        response = self.client.post('/api/employees/bulk-delete/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deactivated'], 1)
        self.assertEqual(response.data['already_inactive'], 1)
    
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
        self.assertIsNone(response.data['previous'])
    
    def test_pagination_page_size_parameter(self):
        """Test that page_size parameter works."""
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
        
        response = self.client.get('/api/employees/?page_size=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)