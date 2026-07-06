"""
Leave Domain Service

This service enforces all leave request business rules and invariants.
It operates purely on domain entities and knows nothing about databases or HTTP.

Architecture Rule: Domain services raise DomainException or ValueError,
never HTTP exceptions. The Presentation layer catches these and converts to HTTP responses.
"""

from typing import List, Dict, Any
from datetime import date
from uuid import UUID

from apps.common.exceptions import (
    LeaveOverlapException,
    InvalidLeaveStatusException,
)
from apps.leave.domain.entities.leave_request import LeaveRequest


class LeaveService:
    """
    Leave domain service - enforces all leave request business rules.
    
    This service validates leave requests and their status transitions.
    """
    
    VALID_LEAVE_TYPES = ['ANNUAL', 'SICK', 'UNPAID', 'MATERNITY']
    VALID_STATUSES = ['PENDING', 'APPROVED', 'REJECTED']
    
    @staticmethod
    def validate_dates(start_date: date, end_date: date) -> None:
        """
        Validate that leave dates are valid.
        
        Business Rule:
        - end_date must be greater than or equal to start_date
        
        Args:
            start_date: The start date of the leave
            end_date: The end date of the leave
            
        Raises:
            ValueError: If end_date is before start_date
        """
        if end_date < start_date:
            raise ValueError(
                f"end_date ({end_date}) must be greater than or equal to start_date ({start_date})"
            )
    
    @staticmethod
    def check_overlap(
        new_start: date,
        new_end: date,
        existing_leaves: List[LeaveRequest]
    ) -> None:
        """
        Check if a new leave request overlaps with existing approved leaves.
        
        Business Rule:
        - A leave request cannot be submitted if the employee already has
          an APPROVED leave that overlaps the requested dates
        
        Args:
            new_start: The start date of the new leave request
            new_end: The end date of the new leave request
            existing_leaves: List of existing leave requests for the employee
            
        Raises:
            LeaveOverlapException: If the new leave overlaps with an approved leave
        """
        for leave in existing_leaves:
            # Only check against approved leaves
            if leave.status == 'APPROVED':
                # Check for overlap: not (new_end < leave.start_date or new_start > leave.end_date)
                if not (new_end < leave.start_date or new_start > leave.end_date):
                    raise LeaveOverlapException(
                        f"Leave request overlaps with approved leave "
                        f"from {leave.start_date} to {leave.end_date} "
                        f"(type: {leave.leave_type})"
                    )
    
    @staticmethod
    def validate_status_transition(leave: LeaveRequest, action: str) -> None:
        """
        Validate that a status transition is allowed.
        
        Business Rule:
        - Only PENDING requests can be approved or rejected
        
        Args:
            leave: The leave request entity
            action: The action being performed ('approve' or 'reject')
            
        Raises:
            InvalidLeaveStatusException: If the transition is not allowed
        """
        if leave.status != 'PENDING':
            raise InvalidLeaveStatusException(
                f"Cannot {action} a leave request with status '{leave.status}'. "
                f"Only PENDING requests can be {action}d."
            )
    
    @staticmethod
    def validate_submit(leave_data: Dict[str, Any]) -> None:
        """
        Validate leave request submission data.
        
        Business Rules:
        1. Leave type must be valid (ANNUAL, SICK, UNPAID, MATERNITY)
        2. Employee ID must be provided
        3. Start and end dates must be valid
        
        Args:
            leave_data: Dictionary containing leave request data
            
        Raises:
            ValueError: If any validation rule is violated
        """
        # Validate leave type
        leave_type = leave_data.get('leave_type')
        if leave_type not in LeaveService.VALID_LEAVE_TYPES:
            raise ValueError(
                f"leave_type must be one of: {', '.join(LeaveService.VALID_LEAVE_TYPES)}"
            )
        
        # Validate employee ID
        employee_id = leave_data.get('employee_id')
        if not employee_id:
            raise ValueError("employee_id is required")
        
        # Validate dates are provided and valid
        start_date = leave_data.get('start_date')
        end_date = leave_data.get('end_date')
        
        if not start_date:
            raise ValueError("start_date is required")
        if not end_date:
            raise ValueError("end_date is required")
        
        # The entity's __post_init__ will validate date order,
        # but we can also check here to provide better error messages
        if isinstance(start_date, date) and isinstance(end_date, date):
            if end_date < start_date:
                raise ValueError(
                    f"end_date ({end_date}) must be greater than or equal to start_date ({start_date})"
                )
    
    @staticmethod
    def calculate_leave_duration(start_date: date, end_date: date) -> int:
        """
        Calculate the duration of a leave request in days (inclusive).
        
        Args:
            start_date: The start date of the leave
            end_date: The end date of the leave
            
        Returns:
            int: Number of days (inclusive)
        """
        return (end_date - start_date).days + 1
    
    @staticmethod
    def is_on_leave(leave: LeaveRequest, as_of_date: date) -> bool:
        """
        Check if an employee is on leave on a specific date.
        
        Args:
            leave: The leave request entity
            as_of_date: The date to check
            
        Returns:
            bool: True if the employee is on leave on that date
        """
        return (
            leave.status == 'APPROVED' and
            leave.start_date <= as_of_date <= leave.end_date
        )
    
    @staticmethod
    def is_approved_leave(leave: LeaveRequest) -> bool:
        """
        Check if a leave request is approved.
        
        Args:
            leave: The leave request entity
            
        Returns:
            bool: True if the leave is approved
        """
        return leave.status == 'APPROVED'
    
    @staticmethod
    def is_pending_leave(leave: LeaveRequest) -> bool:
        """
        Check if a leave request is pending.
        
        Args:
            leave: The leave request entity
            
        Returns:
            bool: True if the leave is pending
        """
        return leave.status == 'PENDING'
    
    @staticmethod
    def is_rejected_leave(leave: LeaveRequest) -> bool:
        """
        Check if a leave request is rejected.
        
        Args:
            leave: The leave request entity
            
        Returns:
            bool: True if the leave is rejected
        """
        return leave.status == 'REJECTED'