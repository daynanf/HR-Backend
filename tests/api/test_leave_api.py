"""
API Tests for Leave Request Endpoints

These tests verify the full request-response cycle for leave operations.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from uuid import uuid4

from apps.departments.infrastructure.models import DepartmentModel
from apps.employees.infrastructure.models import EmployeeModel
from apps.leave.infrastructure.models import LeaveRequestModel


class TestLeaveAPI(TestCase):
    """Test Leave API endpoints."""
    
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
        
        # Create another employee (for testing multi-employee scenarios)
        self.employee2 = EmployeeModel.objects.create(
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
    
    def test_submit_leave_request_succeeds(self):
        """Test that POST /api/leave/ submits a leave request."""
        data = {
            'employee_id': str(self.employee.id),
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
            'reason': 'Family vacation',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['employee_id'], str(self.employee.id))
        self.assertEqual(response.data['leave_type'], 'ANNUAL')
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['reason'], 'Family vacation')
        self.assertIsNone(response.data['reviewed_by'])
        self.assertIsNone(response.data['reviewed_at'])
    
    def test_submit_leave_request_without_reason_succeeds(self):
        """Test that submitting a leave request without reason works."""
        data = {
            'employee_id': str(self.employee.id),
            'leave_type': 'SICK',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['leave_type'], 'SICK')
        self.assertIsNone(response.data['reason'])
    
    def test_submit_leave_with_end_date_before_start_date_returns_400(self):
        """Test that end_date before start_date returns 400."""
        data = {
            'employee_id': str(self.employee.id),
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-15',
            'end_date': '2025-06-10',  # End before start
            'reason': 'Invalid dates',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_leave_with_missing_employee_id_returns_400(self):
        """Test that missing employee_id returns 400."""
        data = {
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_leave_with_invalid_leave_type_returns_400(self):
        """Test that invalid leave type returns 400."""
        data = {
            'employee_id': str(self.employee.id),
            'leave_type': 'INVALID',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
        }
        
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_submit_overlapping_leave_returns_400(self):
        """Test that overlapping leave requests return 400."""
        # Submit first leave
        data1 = {
            'employee_id': str(self.employee.id),
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
            'reason': 'First leave',
        }
        # FIX: Add format='json'
        response1 = self.client.post('/api/leave/', data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Approve the first leave
        leave_id = response1.data['id']
        # FIX: Add format='json'
        self.client.patch(f'/api/leave/{leave_id}/approve/', {'reviewed_by': str(self.employee.id)}, format='json')
        
        # Submit overlapping leave
        data2 = {
            'employee_id': str(self.employee.id),
            'leave_type': 'SICK',
            'start_date': '2025-06-12',
            'end_date': '2025-06-18',
            'reason': 'Overlapping leave',
        }
        # FIX: Add format='json'
        response2 = self.client.post('/api/leave/', data2, format='json')
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response2.data)
    
    def test_submit_non_overlapping_leave_after_approved_succeeds(self):
        """Test that non-overlapping leave after approved leave works."""
        # Submit first leave
        data1 = {
            'employee_id': str(self.employee.id),
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
            'reason': 'First leave',
        }
        # FIX: Add format='json'
        response1 = self.client.post('/api/leave/', data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Approve the first leave
        leave_id = response1.data['id']
        # FIX: Add format='json'
        self.client.patch(f'/api/leave/{leave_id}/approve/', {'reviewed_by': str(self.employee.id)}, format='json')
        
        # Submit non-overlapping leave
        data2 = {
            'employee_id': str(self.employee.id),
            'leave_type': 'SICK',
            'start_date': '2025-06-20',
            'end_date': '2025-06-25',
            'reason': 'Non-overlapping leave',
        }
        # FIX: Add format='json'
        response2 = self.client.post('/api/leave/', data2, format='json')
        
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['status'], 'PENDING')
    
    def test_list_leave_requests_returns_paginated_response(self):
        """Test that GET /api/leave/ returns paginated response."""
        # Create some leave requests
        for i in range(3):
            LeaveRequestModel.objects.create(
                id=uuid4(),
                employee=self.employee,
                leave_type='ANNUAL',
                start_date=date(2025, 6, 10 + i),
                end_date=date(2025, 6, 15 + i),
                status='PENDING',
            )
        
        response = self.client.get('/api/leave/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 3)
    
    def test_list_leave_requests_with_status_filter(self):
        """Test that status filter works."""
        # Create pending leave
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=date(2025, 6, 10),
            end_date=date(2025, 6, 15),
            status='PENDING',
        )
        
        # Create approved leave
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='SICK',
            start_date=date(2025, 6, 20),
            end_date=date(2025, 6, 25),
            status='APPROVED',
        )
        
        response = self.client.get('/api/leave/?status=APPROVED')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['status'], 'APPROVED')
    
    def test_list_leave_requests_with_department_filter(self):
        """Test that department filter works."""
        # Create another department
        dept2 = DepartmentModel.objects.create(
            code='HR',
            name='Human Resources',
            is_active=True,
        )
        
        # Create employee in HR
        hr_employee = EmployeeModel.objects.create(
            id=uuid4(),
            employee_number='EMP-003',
            first_name='Chala',
            last_name='Girma',
            email='chala@company.com',
            department=dept2,
            job_title='HR Manager',
            employment_type='FULL_TIME',
            hire_date=date(2023, 1, 15),
            is_active=True,
        )
        
        # Create leave for engineering employee
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=date(2025, 6, 10),
            end_date=date(2025, 6, 15),
            status='PENDING',
        )
        
        # Create leave for HR employee
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=hr_employee,
            leave_type='SICK',
            start_date=date(2025, 6, 20),
            end_date=date(2025, 6, 25),
            status='PENDING',
        )
        
        response = self.client.get('/api/leave/?department=ENG')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_approve_leave_request_succeeds(self):
        """Test that PATCH /api/leave/{id}/approve/ approves a leave request."""
        # Submit a leave request
        data = {
            'employee_id': str(self.employee.id),
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
        }
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        leave_id = response.data['id']
        
        # Approve it
        # FIX: Add format='json'
        response = self.client.patch(f'/api/leave/{leave_id}/approve/', {'reviewed_by': str(self.employee.id)}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'APPROVED')
        self.assertEqual(response.data['reviewed_by'], str(self.employee.id))
        self.assertIsNotNone(response.data['reviewed_at'])
    
    def test_approve_non_pending_leave_returns_400(self):
        """Test that approving a non-pending leave returns 400."""
        # Create an approved leave directly in database
        leave = LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=date(2025, 6, 10),
            end_date=date(2025, 6, 15),
            status='APPROVED',
        )
        
        # FIX: Add format='json'
        response = self.client.patch(f'/api/leave/{leave.id}/approve/', {'reviewed_by': str(self.employee.id)}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_reject_leave_request_succeeds(self):
        """Test that PATCH /api/leave/{id}/reject/ rejects a leave request."""
        # Submit a leave request
        data = {
            'employee_id': str(self.employee.id),
            'leave_type': 'ANNUAL',
            'start_date': '2025-06-10',
            'end_date': '2025-06-15',
        }
        # FIX: Add format='json'
        response = self.client.post('/api/leave/', data, format='json')
        leave_id = response.data['id']
        
        # Reject it
        # FIX: Add format='json'
        response = self.client.patch(f'/api/leave/{leave_id}/reject/', {'reviewed_by': str(self.employee.id)}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'REJECTED')
        self.assertEqual(response.data['reviewed_by'], str(self.employee.id))
        self.assertIsNotNone(response.data['reviewed_at'])
    
    def test_reject_non_pending_leave_returns_400(self):
        """Test that rejecting a non-pending leave returns 400."""
        # Create an approved leave directly in database
        leave = LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=date(2025, 6, 10),
            end_date=date(2025, 6, 15),
            status='APPROVED',
        )
        
        # FIX: Add format='json'
        response = self.client.patch(f'/api/leave/{leave.id}/reject/', {'reviewed_by': str(self.employee.id)}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_approve_nonexistent_leave_returns_404(self):
        """Test that approving a nonexistent leave returns 404."""
        # FIX: Add format='json'
        response = self.client.patch(f'/api/leave/{uuid4()}/approve/', {'reviewed_by': str(self.employee.id)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_on_leave_count_returns_correct_count(self):
        """Test that GET /api/leave/on-leave-count/ returns correct count."""
        today = date.today()
        
        # Create approved leave for today
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
            status='APPROVED',
        )
        
        # Create approved leave for another employee for today
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee2,
            leave_type='SICK',
            start_date=today,
            end_date=today + timedelta(days=2),
            status='APPROVED',
        )
        
        # Create pending leave (should not be counted)
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='UNPAID',
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            status='PENDING',
        )
        
        response = self.client.get('/api/leave/on-leave-count/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('on_leave_count', response.data)
        self.assertIn('as_of', response.data)
        self.assertEqual(response.data['on_leave_count'], 2)
        self.assertEqual(response.data['as_of'], str(today))
    
    def test_on_leave_count_with_no_approved_leaves(self):
        """Test that on-leave-count returns 0 when no one is on leave."""
        today = date.today()
        
        # Create only pending leaves
        LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=today,
            end_date=today + timedelta(days=1),
            status='PENDING',
        )
        
        response = self.client.get('/api/leave/on-leave-count/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['on_leave_count'], 0)
        self.assertEqual(response.data['as_of'], str(today))
    
    def test_retrieve_leave_request_succeeds(self):
        """Test that GET /api/leave/{id}/ retrieves a leave request."""
        leave = LeaveRequestModel.objects.create(
            id=uuid4(),
            employee=self.employee,
            leave_type='ANNUAL',
            start_date=date(2025, 6, 10),
            end_date=date(2025, 6, 15),
            status='PENDING',
            reason='Family vacation',
        )
        
        response = self.client.get(f'/api/leave/{leave.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(leave.id))
        self.assertEqual(response.data['leave_type'], 'ANNUAL')
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['reason'], 'Family vacation')
    
    def test_retrieve_nonexistent_leave_returns_404(self):
        """Test that retrieving a nonexistent leave request returns 404."""
        response = self.client.get(f'/api/leave/{uuid4()}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_on_leave_count_uses_today_date_not_hardcoded(self):
        """Test that on-leave-count uses today's date (not hardcoded)."""
        response = self.client.get('/api/leave/on-leave-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('as_of', response.data)
        self.assertEqual(response.data['as_of'], str(date.today()))