"""
Approve/Reject Leave Request Command Handler

This is the application service for approving or rejecting leave requests.
It orchestrates domain services and repositories to execute the use case.
"""

import logging
from uuid import UUID
from typing import Dict, Any

from apps.common.exceptions import LeaveNotFoundException, InvalidLeaveStatusException
from apps.leave.domain.ports.leave_port import LeavePort
from apps.leave.domain.services.leave_service import LeaveService

logger = logging.getLogger(__name__)


class ApproveLeaveCommand:
    """
    Use case: Approve or reject a pending leave request.
    
    This command handler:
    1. Retrieves the existing leave request
    2. Validates status transition via LeaveService
    3. Delegates to repository for approval or rejection
    """
    
    def __init__(self, repository: LeavePort):
        """
        Initialize the command with a repository.
        
        Args:
            repository: LeavePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, leave_id: UUID, reviewed_by: UUID, action: str = 'approve') -> LeaveRequest:
        """
        Execute the approve/reject leave request use case.
        
        Args:
            leave_id: UUID of the leave request
            reviewed_by: UUID of the employee who reviewed it
            action: 'approve' or 'reject'
            
        Returns:
            LeaveRequest: The updated leave request entity
            
        Raises:
            LeaveNotFoundException: If leave request doesn't exist
            InvalidLeaveStatusException: If status transition is invalid
        """
        logger.info(f"{action.capitalize()}ing leave request: {leave_id}")
        
        try:
            # Retrieve existing leave request
            existing = self.repository.get_by_id(leave_id)
            if not existing:
                raise LeaveNotFoundException(f"Leave request {leave_id} not found")
            
            # Validate status transition via domain service
            LeaveService.validate_status_transition(existing, action)
            
            # Delegate to repository
            if action == 'approve':
                result = self.repository.approve(leave_id, reviewed_by)
            else:
                result = self.repository.reject(leave_id, reviewed_by)
            
            logger.info(f"Leave request {action}d successfully: {result.id}")
            return result
            
        except (LeaveNotFoundException, InvalidLeaveStatusException) as e:
            logger.warning(f"Leave request {action} failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error {action}ing leave request: {str(e)}")
            raise