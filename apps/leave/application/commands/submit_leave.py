"""
Submit Leave Request Command Handler

This is the application service for submitting new leave requests.
It orchestrates domain services and repositories to execute the use case.
"""

import logging
from uuid import uuid4
from typing import Dict, Any

from apps.common.exceptions import LeaveOverlapException
from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.domain.ports.leave_port import LeavePort
from apps.leave.domain.services.leave_service import LeaveService

logger = logging.getLogger(__name__)


class SubmitLeaveCommand:
    """
    Use case: Submit a new leave request with business rule validation.
    
    This command handler:
    1. Validates dates
    2. Checks for overlaps with approved leave
    3. Creates and persists the LeaveRequest entity
    """
    
    def __init__(self, repository: LeavePort):
        """
        Initialize the command with a repository.
        
        Args:
            repository: LeavePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, data: Dict[str, Any]) -> LeaveRequest:
        """
        Execute the submit leave request use case.
        
        Args:
            data: Dictionary containing leave request data:
                - employee_id: UUID
                - leave_type: str (ANNUAL, SICK, UNPAID, MATERNITY)
                - start_date: date
                - end_date: date
                - reason: Optional[str]
            
        Returns:
            LeaveRequest: The created leave request entity
            
        Raises:
            LeaveOverlapException: If leave overlaps with approved leave
            ValueError: If validation fails
        """
        logger.info(f"Submitting leave request for employee: {data.get('employee_id')}")
        
        try:
            # Validate dates via domain service
            LeaveService.validate_dates(data['start_date'], data['end_date'])
            
            # Check for overlaps
            existing_leaves = self.repository.list_for_employee(data['employee_id'])
            LeaveService.check_overlap(
                data['start_date'],
                data['end_date'],
                existing_leaves
            )
            
            # Create the leave request entity
            leave = LeaveRequest(
                id=uuid4(),
                employee_id=data['employee_id'],
                leave_type=data['leave_type'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                status='PENDING',
                reason=data.get('reason'),
                reviewed_by=None,
                reviewed_at=None,
            )
            
            # Persist via repository
            created = self.repository.submit(leave)
            
            logger.info(f"Leave request submitted successfully: {created.id}")
            return created
            
        except (LeaveOverlapException, ValueError) as e:
            logger.warning(f"Leave request submission failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error submitting leave request: {str(e)}")
            raise