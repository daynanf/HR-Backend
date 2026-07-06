"""
Get Employee Query Handler

This is the application service for retrieving a single employee.
It orchestrates repositories to execute the read use case.
"""

import logging
from uuid import UUID
from typing import Optional

from apps.common.exceptions import EmployeeNotFoundException
from apps.employees.domain.entities.employee import Employee
from apps.employees.domain.ports.employee_port import EmployeePort

logger = logging.getLogger(__name__)


class GetEmployeeQuery:
    """
    Use case: Retrieve a single employee by ID.
    
    This query handler:
    1. Retrieves an employee by UUID
    2. Returns the employee or raises an exception
    """
    
    def __init__(self, repository: EmployeePort):
        """
        Initialize the query with a repository.
        
        Args:
            repository: EmployeePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, employee_id: UUID) -> Employee:
        """
        Execute the get employee query.
        
        Args:
            employee_id: UUID of the employee to retrieve
            
        Returns:
            Employee: The employee entity
            
        Raises:
            EmployeeNotFoundException: If employee doesn't exist
        """
        logger.debug(f"Retrieving employee with id: {employee_id}")
        
        try:
            employee = self.repository.get_by_id(employee_id)
            if not employee:
                raise EmployeeNotFoundException(f"Employee {employee_id} not found")
            
            return employee
            
        except EmployeeNotFoundException as e:
            logger.warning(f"Employee not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving employee: {str(e)}")
            raise