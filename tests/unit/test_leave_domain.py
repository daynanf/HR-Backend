"""
Unit Tests for Leave Domain Layer

These tests verify that all leave request business rules are enforced correctly.
"""

import unittest
from datetime import date, timedelta
from uuid import uuid4

from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.domain.services.leave_service import LeaveService
from apps.leave.application.commands.submit_leave import SubmitLeaveCommand
from apps.leave.application.commands.approve_leave import ApproveLeaveCommand
from apps.leave.application.queries.get_on_leave_count import GetOnLeaveCountQuery
from apps.common.exceptions import (
    LeaveOverlapException,
    InvalidLeaveStatusException,
    LeaveNotFoundException,
)
from tests.unit.fake_repositories import FakeLeaveRepository


class TestLeaveDomain(unittest.TestCase):
    """Test leave request domain business rules."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.repo = FakeLeaveRepository()
        self.employee_id = uuid4()
        self.valid_leave_data = {
            'employee_id': self.employee_id,
            'leave_type': 'ANNUAL',
            'start_date': date(2025, 6, 10),
            'end_date': date(2025, 6, 15),
            'reason': 'Family vacation',
        }
    
    def test_submit_valid_leave_succeeds(self):
        """Test that submitting a valid leave request works."""
        command = SubmitLeaveCommand(self.repo)
        leave = command.execute(self.valid_leave_data)
        
        self.assertIsNotNone(leave.id)
        self.assertEqual(leave.employee_id, self.employee_id)
        self.assertEqual(leave.leave_type, 'ANNUAL')
        self.assertEqual(leave.status, 'PENDING')
        self.assertEqual(leave.start_date, date(2025, 6, 10))
        self.assertEqual(leave.end_date, date(2025, 6, 15))
    
    def test_end_date_before_start_date_raises_exception(self):
        """Test that end_date before start_date raises ValueError."""
        invalid_data = self.valid_leave_data.copy()
        invalid_data['start_date'] = date(2025, 6, 15)
        invalid_data['end_date'] = date(2025, 6, 10)
        
        command = SubmitLeaveCommand(self.repo)
        with self.assertRaises(ValueError):
            command.execute(invalid_data)
    
    def test_overlap_with_approved_leave_raises_exception(self):
        """Test that overlapping with approved leave raises exception."""
        # Submit first leave and approve it
        command = SubmitLeaveCommand(self.repo)
        leave1 = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approve_command.execute(leave1.id, self.employee_id, 'approve')
        
        # Try to submit overlapping leave
        overlapping_data = self.valid_leave_data.copy()
        overlapping_data['start_date'] = date(2025, 6, 12)
        overlapping_data['end_date'] = date(2025, 6, 18)
        overlapping_data['leave_type'] = 'SICK'
        
        with self.assertRaises(LeaveOverlapException):
            command.execute(overlapping_data)
    
    def test_non_overlapping_leave_after_approved_succeeds(self):
        """Test that non-overlapping leave after approved leave works."""
        command = SubmitLeaveCommand(self.repo)
        leave1 = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approve_command.execute(leave1.id, self.employee_id, 'approve')
        
        # Submit non-overlapping leave
        non_overlapping_data = self.valid_leave_data.copy()
        non_overlapping_data['start_date'] = date(2025, 6, 20)
        non_overlapping_data['end_date'] = date(2025, 6, 25)
        non_overlapping_data['leave_type'] = 'SICK'
        
        leave2 = command.execute(non_overlapping_data)
        self.assertEqual(leave2.status, 'PENDING')
    
    def test_non_overlapping_leave_before_approved_succeeds(self):
        """Test that non-overlapping leave before approved leave works."""
        command = SubmitLeaveCommand(self.repo)
        leave1 = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approve_command.execute(leave1.id, self.employee_id, 'approve')
        
        # Submit non-overlapping leave
        non_overlapping_data = self.valid_leave_data.copy()
        non_overlapping_data['start_date'] = date(2025, 6, 1)
        non_overlapping_data['end_date'] = date(2025, 6, 5)
        non_overlapping_data['leave_type'] = 'SICK'
        
        leave2 = command.execute(non_overlapping_data)
        self.assertEqual(leave2.status, 'PENDING')
    
    def test_approve_pending_leave_succeeds(self):
        """Test that approving a pending leave request works."""
        command = SubmitLeaveCommand(self.repo)
        leave = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approved = approve_command.execute(leave.id, self.employee_id, 'approve')
        
        self.assertEqual(approved.status, 'APPROVED')
        self.assertEqual(approved.reviewed_by, self.employee_id)
        self.assertIsNotNone(approved.reviewed_at)
    
    def test_reject_pending_leave_succeeds(self):
        """Test that rejecting a pending leave request works."""
        command = SubmitLeaveCommand(self.repo)
        leave = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        rejected = approve_command.execute(leave.id, self.employee_id, 'reject')
        
        self.assertEqual(rejected.status, 'REJECTED')
        self.assertEqual(rejected.reviewed_by, self.employee_id)
        self.assertIsNotNone(rejected.reviewed_at)
    
    def test_approve_already_approved_leave_raises_exception(self):
        """Test that approving an already approved leave raises exception."""
        command = SubmitLeaveCommand(self.repo)
        leave = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approve_command.execute(leave.id, self.employee_id, 'approve')
        
        # Try to approve again
        with self.assertRaises(InvalidLeaveStatusException):
            approve_command.execute(leave.id, self.employee_id, 'approve')
    
    def test_reject_already_approved_leave_raises_exception(self):
        """Test that rejecting an already approved leave raises exception."""
        command = SubmitLeaveCommand(self.repo)
        leave = command.execute(self.valid_leave_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approve_command.execute(leave.id, self.employee_id, 'approve')
        
        # Try to reject
        with self.assertRaises(InvalidLeaveStatusException):
            approve_command.execute(leave.id, self.employee_id, 'reject')
    
    def test_approve_nonexistent_leave_raises_exception(self):
        """Test that approving a nonexistent leave raises exception."""
        approve_command = ApproveLeaveCommand(self.repo)
        with self.assertRaises(LeaveNotFoundException):
            approve_command.execute(uuid4(), self.employee_id, 'approve')
    
    def test_get_on_leave_count(self):
        """Test that on-leave count returns correct number."""
        command = SubmitLeaveCommand(self.repo)
        
        # Create an approved leave covering today
        today = date.today()
        leave1_data = self.valid_leave_data.copy()
        leave1_data['start_date'] = today - timedelta(days=2)
        leave1_data['end_date'] = today + timedelta(days=2)
        leave1 = command.execute(leave1_data)
        
        approve_command = ApproveLeaveCommand(self.repo)
        approve_command.execute(leave1.id, self.employee_id, 'approve')
        
        # Create another approved leave for a different employee
        employee2_id = uuid4()
        leave2_data = self.valid_leave_data.copy()
        leave2_data['employee_id'] = employee2_id
        leave2_data['start_date'] = today - timedelta(days=1)
        leave2_data['end_date'] = today + timedelta(days=1)
        leave2 = command.execute(leave2_data)
        
        approve_command.execute(leave2.id, employee2_id, 'approve')
        
        # Get on-leave count
        query = GetOnLeaveCountQuery(self.repo)
        result = query.execute()
        
        self.assertEqual(result['on_leave_count'], 2)
        self.assertEqual(result['as_of'], str(today))
    
    def test_invalid_leave_type_raises_exception(self):
        """Test that invalid leave type raises ValueError."""
        invalid_data = self.valid_leave_data.copy()
        invalid_data['leave_type'] = 'INVALID'
        
        command = SubmitLeaveCommand(self.repo)
        with self.assertRaises(ValueError):
            command.execute(invalid_data)


if __name__ == '__main__':
    unittest.main()