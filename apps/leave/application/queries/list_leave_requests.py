"""
List Leave Requests Query Handler

This is the application service for listing leave requests with filters.
"""

import logging
from typing import List, Dict, Any

from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.domain.ports.leave_port import LeavePort

logger = logging.getLogger(__name__)


class ListLeaveRequestsQuery:
    """
    Use case: List leave requests with optional filters.
    """
    
    def __init__(self, repository: LeavePort):
        self.repository = repository
    
    def execute(self, filters: Dict[str, str]) -> List[LeaveRequest]:
        """
        Execute the list leave requests query.
        
        Args:
            filters: Dictionary of filter parameters:
                - status: Filter by status (PENDING, APPROVED, REJECTED)
                - department: Filter by department code
            
        Returns:
            List[LeaveRequest]: List of leave requests matching the filters
        """
        logger.debug(f"Listing leave requests with filters: {filters}")
        
        try:
            clean_filters = {k: v for k, v in filters.items() if v}
            leaves = self.repository.list_all(clean_filters)
            logger.debug(f"Found {len(leaves)} leave requests")
            return leaves
            
        except Exception as e:
            logger.error(f"Error listing leave requests: {str(e)}")
            raise