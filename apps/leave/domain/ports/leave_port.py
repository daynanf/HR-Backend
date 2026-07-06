"""
Leave Port Interface

This defines the contract between the Application layer and the Infrastructure layer.
The infrastructure layer implements this interface using Django ORM.

Architecture Rule: Port interfaces are abstract base classes defined in the domain layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import date
from uuid import UUID

from apps.leave.domain.entities.leave_request import LeaveRequest


class LeavePort(ABC):
    """
    Interface for Leave Repository operations.
    """
    
    @abstractmethod
    def submit(self, leave: LeaveRequest) -> LeaveRequest:
        """
        Submit a new leave request.
        
        Args:
            leave: The LeaveRequest entity to persist
            
        Returns:
            LeaveRequest: The persisted leave request
            
        Raises:
            LeaveOverlapException: If the leave overlaps with an approved leave
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[LeaveRequest]:
        """
        Retrieve a leave request by UUID.
        
        Args:
            id: The leave request's UUID
            
        Returns:
            Optional[LeaveRequest]: The leave request if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_for_employee(self, employee_id: UUID) -> List[LeaveRequest]:
        """
        List all leave requests for a specific employee.
        
        Args:
            employee_id: The employee's UUID
            
        Returns:
            List[LeaveRequest]: List of all leave requests for the employee
        """
        pass
    
    @abstractmethod
    def approve(self, id: UUID, reviewed_by: UUID) -> LeaveRequest:
        """
        Approve a pending leave request.
        
        Args:
            id: The leave request's UUID
            reviewed_by: The UUID of the employee who approved it
            
        Returns:
            LeaveRequest: The approved leave request
            
        Raises:
            LeaveNotFoundException: If the leave request doesn't exist
            InvalidLeaveStatusException: If the leave request is not PENDING
        """
        pass
    
    @abstractmethod
    def reject(self, id: UUID, reviewed_by: UUID) -> LeaveRequest:
        """
        Reject a pending leave request.
        
        Args:
            id: The leave request's UUID
            reviewed_by: The UUID of the employee who rejected it
            
        Returns:
            LeaveRequest: The rejected leave request
            
        Raises:
            LeaveNotFoundException: If the leave request doesn't exist
            InvalidLeaveStatusException: If the leave request is not PENDING
        """
        pass
    
    @abstractmethod
    def get_on_leave_count(self, as_of_date: date) -> int:
        """
        Count employees on approved leave as of a specific date.
        
        Args:
            as_of_date: The date to count on-leave employees
            
        Returns:
            int: Number of employees on approved leave on the given date
        """
        pass
    
    @abstractmethod
    def list_all(self, filters: Dict[str, str]) -> List[LeaveRequest]:
        """
        List all leave requests with optional filters.
        
        Args:
            filters: Dictionary of filter parameters
                - status: Filter by status (PENDING, APPROVED, REJECTED)
                - department: Filter by department code
                
        Returns:
            List[LeaveRequest]: List of leave requests matching the filters
        """
        pass