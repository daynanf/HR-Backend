"""
Get On-Leave Count Query Handler

This is the application service for counting employees on approved leave today.
"""

import logging
from datetime import date
from typing import Dict

from apps.leave.domain.ports.leave_port import LeavePort

logger = logging.getLogger(__name__)


class GetOnLeaveCountQuery:
    """
    Use case: Count employees on approved leave as of today.
    
    This query handler:
    1. Gets today's date (never hardcoded)
    2. Delegates count to the repository
    3. Returns the count with the as_of date
    """
    
    def __init__(self, repository: LeavePort):
        self.repository = repository
    
    def execute(self) -> Dict[str, str]:
        """
        Execute the get on-leave count query.
        
        Returns:
            Dict[str, str]: Dictionary with:
                - on_leave_count: Number of employees on leave
                - as_of: Today's date as string (YYYY-MM-DD)
        """
        try:
            # Get today's date - NEVER hardcode this
            today = date.today()
            logger.debug(f"Getting on-leave count as of: {today}")
            
            count = self.repository.get_on_leave_count(today)
            
            logger.debug(f"Found {count} employees on leave")
            return {
                'on_leave_count': count,
                'as_of': str(today),
            }
            
        except Exception as e:
            logger.error(f"Error getting on-leave count: {str(e)}")
            raise