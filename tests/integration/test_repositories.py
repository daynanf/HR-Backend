"""
Integration Tests for Repository Layer

These tests verify that repositories work correctly with the database.
They use Django's TestCase with a real SQLite test database.

Architecture Rule: Integration tests use Django's TestCase.
"""

from django.test import TestCase
from datetime import date, timedelta
from uuid import uuid4

from apps.employees.domain.entities.employee import Employee
from apps.employees.infrastructure.repository import EmployeeRepository

from apps.departments.domain.entities.department import Department
from apps.departments.infrastructure.repository import DepartmentRepository
from apps.departments.infrastructure.models import DepartmentModel

from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.infrastructure.repository import LeaveRepository
from apps.leave.infrastructure.models import LeaveRequestModel

from apps.common.exceptions import (
    DuplicateEmailException,
    DuplicateEmployeeNumberException,
    EmployeeNotFoundException,
    DepartmentHasActiveEmployeesException,
)


class TestEmployeeRepository(TestCase):
    """Test EmployeeRepository with real database."""
    
    def setUp(self):
        """Set up test fixtures in the database."""
        # Create a department
        self.dept_repo = DepartmentRepository()
        self.dept = self.dept_repo.create(
            Department(code='ENG', name='Engineering')
        )
        
        self.repo = EmployeeRepository()
        self.employee_data = {
            'employee_number': 'EMP-001',
            'first_name': 'Abebe',
            'last_name': 'Kebede',
            'email': 'abebe@test.com',
            'department_id': self.dept.id,
            'job_title': 'Software Engineer',
            'employment_type': 'FULL_TIME',
            'hire_date': date(2023, 1, 15),
            'is_active': True,
        }
    
    def test_create_employee_succeeds(self):
        """Test creating an employee in the database."""
        employee = Employee(**self.employee_data)
        created = self.repo.create(employee)
        
        self.assertIsNotNone(created.id)
        self.assertEqual(created.employee_number, 'EMP-001')
        self.assertEqual(created.first_name, 'Abebe')
        self.assertTrue(created.is_active)
        self.assertIsNotNone(created.created_at)
    
    def test_create_employee_with_duplicate_email_raises_exception(self):
        """Test that duplicate email raises exception."""
        employee = Employee(**self.employee_data)
        self.repo.create(employee)
        
        duplicate_data = self.employee_data.copy()
        duplicate_data['employee_number'] = 'EMP-002'
        duplicate_data['first_name'] = 'Beyene'
        duplicate_data['last_name'] = 'Tesfaye'
        duplicate_employee = Employee(**duplicate_data)
        
        with self.assertRaises(DuplicateEmailException):
            self.repo.create(duplicate_employee)
    
    def test_create_employee_with_duplicate_number_raises_exception(self):
        """Test that duplicate employee number raises exception."""
        employee = Employee(**self.employee_data)
        self.repo.create(employee)
        
        duplicate_data = self.employee_data.copy()
        duplicate_data['email'] = 'beyene@test.com'
        duplicate_data['first_name'] = 'Beyene'
        duplicate_employee = Employee(**duplicate_data)
        
        with self.assertRaises(DuplicateEmployeeNumberException):
            self.repo.create(duplicate_employee)
    
    def test_get_by_id_returns_correct_employee(self):
        """Test retrieving an employee by ID."""
        employee = Employee(**self.employee_data)
        created = self.repo.create(employee)
        
        fetched = self.repo.get_by_id(created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, created.id)
        self.assertEqual(fetched.email, 'abebe@test.com')
    
    def test_get_by_email_returns_correct_employee(self):
        """Test retrieving an employee by email."""
        employee = Employee(**self.employee_data)
        self.repo.create(employee)
        
        fetched = self.repo.get_by_email('abebe@test.com')
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.first_name, 'Abebe')
        self.assertEqual(fetched.last_name, 'Kebede')
    
    def test_get_by_email_returns_none_if_not_found(self):
        """Test that get_by_email returns None for non-existent email."""
        fetched = self.repo.get_by_email('nonexistent@test.com')
        self.assertIsNone(fetched)
    
    def test_get_by_employee_number_returns_correct_employee(self):
        """Test retrieving an employee by employee number."""
        employee = Employee(**self.employee_data)
        self.repo.create(employee)
        
        fetched = self.repo.get_by_employee_number('EMP-001')
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.email, 'abebe@test.com')
    
    def test_list_active_returns_only_active_employees(self):
        """Test that list_active only returns active employees."""
        employee = Employee(**self.employee_data)
        self.repo.create(employee)
        
        # Create inactive employee
        inactive_data = self.employee_data.copy()
        inactive_data['employee_number'] = 'EMP-002'
        inactive_data['email'] = 'inactive@test.com'
        inactive_data['first_name'] = 'Inactive'
        inactive_data['is_active'] = False
        inactive_employee = Employee(**inactive_data)
        self.repo.create(inactive_employee)
        
        active = self.repo.list_active({})
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].employee_number, 'EMP-001')
    
    def test_soft_delete_excludes_employee_from_list_active(self):
        """Test that soft-deleted employees are excluded from list_active."""
        employee = Employee(**self.employee_data)
        created = self.repo.create(employee)
        
        # Employee should be in active list
        active = self.repo.list_active({})
        self.assertEqual(len(active), 1)
        
        # Soft delete
        self.repo.soft_delete(created.id)
        
        # Employee should not be in active list
        active = self.repo.list_active({})
        self.assertEqual(len(active), 0)
        
        # But still retrievable by ID
        fetched = self.repo.get_by_id(created.id)
        self.assertIsNotNone(fetched)
        self.assertFalse(fetched.is_active)
    
    def test_soft_delete_nonexistent_employee_raises_exception(self):
        """Test that soft deleting nonexistent employee raises exception."""
        with self.assertRaises(EmployeeNotFoundException):
            self.repo.soft_delete(uuid4())
    
    def test_update_employee_succeeds(self):
        """Test updating an employee."""
        employee = Employee(**self.employee_data)
        created = self.repo.create(employee)
        
        created.first_name = 'Beyene'
        created.job_title = 'Senior Software Engineer'
        updated = self.repo.update(created)
        
        self.assertEqual(updated.first_name, 'Beyene')
        self.assertEqual(updated.job_title, 'Senior Software Engineer')
    
    def test_bulk_deactivate_returns_correct_counts(self):
        """Test that bulk deactivate returns correct counts."""
        employee1 = Employee(**self.employee_data)
        self.repo.create(employee1)
        
        employee2_data = self.employee_data.copy()
        employee2_data['employee_number'] = 'EMP-002'
        employee2_data['email'] = 'beyene@test.com'
        employee2_data['first_name'] = 'Beyene'
        employee2 = Employee(**employee2_data)
        self.repo.create(employee2)
        
        # Create an inactive employee
        inactive_data = self.employee_data.copy()
        inactive_data['employee_number'] = 'EMP-003'
        inactive_data['email'] = 'inactive@test.com'
        inactive_data['first_name'] = 'Inactive'
        inactive_data['is_active'] = False
        inactive = Employee(**inactive_data)
        self.repo.create(inactive)
        
        result = self.repo.bulk_deactivate([employee1.id, employee2.id, uuid4()])
        
        self.assertEqual(result['deactivated'], 2)
        self.assertEqual(result['already_inactive'], 0)
        self.assertEqual(result['not_found'], 1)
    
    def test_get_next_employee_number(self):
        """Test getting the next employee number."""
        self.assertEqual(self.repo.get_next_employee_number(), 'EMP-001')
        
        employee = Employee(**self.employee_data)
        self.repo.create(employee)
        
        self.assertEqual(self.repo.get_next_employee_number(), 'EMP-002')


class TestDepartmentRepository(TestCase):
    """Test DepartmentRepository with real database."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo = DepartmentRepository()
        self.valid_dept_data = {
            'code': 'ENG',
            'name': 'Engineering',
            'is_active': True,
        }
    
    def test_create_department_succeeds(self):
        """Test creating a department in the database."""
        department = Department(**self.valid_dept_data)
        created = self.repo.create(department)
        
        self.assertIsNotNone(created.id)
        self.assertEqual(created.code, 'ENG')
        self.assertEqual(created.name, 'Engineering')
        self.assertTrue(created.is_active)
    
    def test_create_duplicate_code_raises_exception(self):
        """Test that duplicate code raises exception."""
        dept1 = Department(**self.valid_dept_data)
        self.repo.create(dept1)
        
        dept2 = Department(**self.valid_dept_data)
        with self.assertRaises(Exception):  # Will be handled by application layer
            self.repo.create(dept2)
    
    def test_deactivate_department_with_active_employees_raises_exception(self):
        """Test that deactivating department with active employees raises exception."""
        dept = Department(**self.valid_dept_data)
        created = self.repo.create(dept)
        
        # Create an employee in this department
        from apps.employees.infrastructure.models import EmployeeModel
        EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-001',
            first_name='Abebe',
            last_name='Kebede',
            email='abebe@test.com',
            department=DepartmentModel.objects.get(id=created.id),
            job_title='Engineer',
            employment_type='FULL_TIME',
            hire_date=date.today(),
            is_active=True,
        )
        
        with self.assertRaises(DepartmentHasActiveEmployeesException):
            self.repo.deactivate(created.id)


class TestLeaveRepository(TestCase):
    """Test LeaveRepository with real database."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a department
        from apps.departments.infrastructure.models import DepartmentModel
        self.dept = DepartmentModel.objects.create(
            code='ENG',
            name='Engineering',
            is_active=True,
        )
        
        # Create an employee
        from apps.employees.infrastructure.models import EmployeeModel
        self.employee = EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-001',
            first_name='Abebe',
            last_name='Kebede',
            email='abebe@test.com',
            department=self.dept,
            job_title='Engineer',
            employment_type='FULL_TIME',
            hire_date=date.today(),
            is_active=True,
        )
        
        self.repo = LeaveRepository()
        self.valid_leave_data = {
            'employee_id': self.employee.id,
            'leave_type': 'ANNUAL',
            'start_date': date(2025, 6, 10),
            'end_date': date(2025, 6, 15),
            'status': 'PENDING',
        }
    
    def test_submit_leave_succeeds(self):
        """Test submitting a leave request."""
        leave = LeaveRequest(**self.valid_leave_data)
        created = self.repo.submit(leave)
        
        self.assertIsNotNone(created.id)
        self.assertEqual(created.employee_id, self.employee.id)
        self.assertEqual(created.status, 'PENDING')
    
    def test_approve_leave_succeeds(self):
        """Test approving a leave request."""
        leave = LeaveRequest(**self.valid_leave_data)
        created = self.repo.submit(leave)
        
        approved = self.repo.approve(created.id, self.employee.id)
        self.assertEqual(approved.status, 'APPROVED')
        self.assertEqual(approved.reviewed_by, self.employee.id)
        self.assertIsNotNone(approved.reviewed_at)
    
    def test_reject_leave_succeeds(self):
        """Test rejecting a leave request."""
        leave = LeaveRequest(**self.valid_leave_data)
        created = self.repo.submit(leave)
        
        rejected = self.repo.reject(created.id, self.employee.id)
        self.assertEqual(rejected.status, 'REJECTED')
        self.assertEqual(rejected.reviewed_by, self.employee.id)
        self.assertIsNotNone(rejected.reviewed_at)
    
    def test_get_on_leave_count_returns_correct_count(self):
        """Test that on-leave count returns correct number."""
        today = date.today()
        
        # Create approved leave for today
        leave1 = LeaveRequest(
            employee_id=self.employee.id,
            leave_type='ANNUAL',
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
            status='PENDING',
        )
        created1 = self.repo.submit(leave1)
        self.repo.approve(created1.id, self.employee.id)
        
        # Create another employee with approved leave
        employee2 = EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-002',
            first_name='Beyene',
            last_name='Tesfaye',
            email='beyene@test.com',
            department=self.dept,
            job_title='Engineer',
            employment_type='FULL_TIME',
            hire_date=date.today(),
            is_active=True,
        )
        
        leave2 = LeaveRequest(
            employee_id=employee2.id,
            leave_type='SICK',
            start_date=today,
            end_date=today + timedelta(days=1),
            status='PENDING',
        )
        created2 = self.repo.submit(leave2)
        self.repo.approve(created2.id, employee2.id)
        
        # Create pending leave (should not be counted)
        leave3 = LeaveRequest(
            employee_id=self.employee.id,
            leave_type='UNPAID',
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            status='PENDING',
        )
        self.repo.submit(leave3)
        
        count = self.repo.get_on_leave_count(today)
        self.assertEqual(count, 2)