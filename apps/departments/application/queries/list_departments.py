"""
List Departments Query Handler

This is the application service for listing all departments.
"""

import logging
from typing import List

from apps.departments.domain.entities.department import Department
from apps.departments.domain.ports.department_port import DepartmentPort

logger = logging.getLogger(__name__)


class ListDepartmentsQuery:
    """
    Use case: List all departments.
    """
    
    def __init__(self, repository: DepartmentPort):
        self.repository = repository
    
    def execute(self) -> List[Department]:
        """
        Execute the list departments query.
        
        Returns:
            List[Department]: List of all departments
        """
        logger.debug("Listing all departments")
        
        try:
            departments = self.repository.list_all()
            logger.debug(f"Found {len(departments)} departments")
            return departments
            
        except Exception as e:
            logger.error(f"Error listing departments: {str(e)}")
            raise