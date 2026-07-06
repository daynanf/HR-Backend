"""
Unit Tests for Department Domain Layer

These tests verify that all department business rules are enforced correctly.
"""

import unittest
from uuid import uuid4

from apps.departments.domain.entities.department import Department
from apps.departments.domain.services.department_service import DepartmentService
from apps.departments.application.commands.create_department import CreateDepartmentCommand
from apps.departments.application.commands.update_department import UpdateDepartmentCommand
from apps.common.exceptions import (
    DepartmentHasActiveEmployeesException,
    DepartmentNotFoundException,
    DuplicateDepartmentCodeException,
)
from tests.unit.fake_repositories import FakeDepartmentRepository


class TestDepartmentDomain(unittest.TestCase):
    """Test department domain business rules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo = FakeDepartmentRepository()
        self.valid_dept_data = {
            'code': 'ENG',
            'name': 'Engineering',
            'description': 'Engineering Department',
        }
    
    def test_create_valid_department_succeeds(self):
        """Test that creating a valid department works."""
        command = CreateDepartmentCommand(self.repo)
        department = command.execute(self.valid_dept_data)
        
        self.assertIsNotNone(department.id)
        self.assertEqual(department.code, 'ENG')
        self.assertEqual(department.name, 'Engineering')
        self.assertTrue(department.is_active)
    
    def test_duplicate_code_raises_exception(self):
        """Test that duplicate department code raises exception."""
        command = CreateDepartmentCommand(self.repo)
        command.execute(self.valid_dept_data)
        
        with self.assertRaises(DuplicateDepartmentCodeException):
            command.execute(self.valid_dept_data)
    
    def test_empty_code_raises_exception(self):
        """Test that empty code raises ValueError."""
        invalid_data = self.valid_dept_data.copy()
        invalid_data['code'] = ''
        
        command = CreateDepartmentCommand(self.repo)
        with self.assertRaises(ValueError):
            command.execute(invalid_data)
    
    def test_empty_name_raises_exception(self):
        """Test that empty name raises ValueError."""
        invalid_data = self.valid_dept_data.copy()
        invalid_data['name'] = ''
        
        command = CreateDepartmentCommand(self.repo)
        with self.assertRaises(ValueError):
            command.execute(invalid_data)
    
    def test_non_alphanumeric_code_raises_exception(self):
        """Test that non-alphanumeric code raises ValueError."""
        invalid_data = self.valid_dept_data.copy()
        invalid_data['code'] = 'ENG-123'
        
        command = CreateDepartmentCommand(self.repo)
        with self.assertRaises(ValueError):
            command.execute(invalid_data)
    
    def test_update_department_succeeds(self):
        """Test that updating a department works."""
        command = CreateDepartmentCommand(self.repo)
        department = command.execute(self.valid_dept_data)
        
        update_command = UpdateDepartmentCommand(self.repo)
        updated = update_command.execute(
            department.id,
            {'name': 'Software Engineering', 'code': 'SOFT'}
        )
        
        self.assertEqual(updated.name, 'Software Engineering')
        self.assertEqual(updated.code, 'SOFT')
    
    def test_update_duplicate_code_raises_exception(self):
        """Test that updating to a duplicate code raises exception."""
        command = CreateDepartmentCommand(self.repo)
        dept1 = command.execute(self.valid_dept_data)
        
        data2 = self.valid_dept_data.copy()
        data2['code'] = 'HR'
        data2['name'] = 'Human Resources'
        dept2 = command.execute(data2)
        
        update_command = UpdateDepartmentCommand(self.repo)
        with self.assertRaises(DuplicateDepartmentCodeException):
            update_command.execute(dept2.id, {'code': 'ENG'})
    
    def test_deactivate_department_with_no_employees_succeeds(self):
        """Test that deactivating a department with no employees works."""
        command = CreateDepartmentCommand(self.repo)
        department = command.execute(self.valid_dept_data)
        
        result = self.repo.deactivate(department.id)
        self.assertTrue(result)
        
        fetched = self.repo.get_by_id(department.id)
        self.assertFalse(fetched.is_active)
    
    def test_deactivate_department_with_active_employees_raises_exception(self):
        """Test that deactivating a department with active employees raises exception."""
        command = CreateDepartmentCommand(self.repo)
        department = command.execute(self.valid_dept_data)
        
        # Add active employees to the department
        self.repo.set_employee_count(department.id, 5)
        
        with self.assertRaises(DepartmentHasActiveEmployeesException):
            self.repo.deactivate(department.id)
    
    def test_department_service_validate_deactivation(self):
        """Test that DepartmentService validates deactivation correctly."""
        # Should not raise for 0 employees
        DepartmentService.validate_deactivation(uuid4(), 0)
        
        # Should raise for > 0 employees
        with self.assertRaises(DepartmentHasActiveEmployeesException):
            DepartmentService.validate_deactivation(uuid4(), 5)


if __name__ == '__main__':
    unittest.main()