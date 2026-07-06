"""
List Employees Query Handler

This is the application service for listing employees with filters.
It orchestrates repositories to execute the read use case.

Architecture Rule: Query handlers handle read operations.
They contain NO HTTP concerns and NO ORM access directly.
"""

import logging
from typing import List, Dict, Any

from apps.employees.domain.entities.employee import Employee
from apps.employees.domain.ports.employee_port import EmployeePort

logger = logging.getLogger(__name__)


class ListEmployeesQuery:
    """
    Use case: List active employees with optional filters.
    
    This query handler:
    1. Accepts filter parameters (search, department)
    2. Delegates filtering to the repository
    3. Returns a list of employee entities
    """
    
    def __init__(self, repository: EmployeePort):
        """
        Initialize the query with a repository.
        
        Args:
            repository: EmployeePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, filters: Dict[str, str]) -> List[Employee]:
        """
        Execute the list employees query.
        
        Args:
            filters: Dictionary of filter parameters:
                - search: Search by first_name or last_name (optional)
                - department: Filter by department code (optional)
            
        Returns:
            List[Employee]: List of active employees matching the filters
        """
        logger.debug(f"Listing employees with filters: {filters}")
        
        try:
            # Clean filters - remove empty values
            clean_filters = {k: v for k, v in filters.items() if v}
            
            # Delegate to repository
            employees = self.repository.list_active(clean_filters)
            
            logger.debug(f"Found {len(employees)} employees matching filters")
            return employees
            
        except Exception as e:
            logger.error(f"Error listing employees: {str(e)}")
            raise