"""
Delete Employee Command Handler (Soft Delete)

This is the application service for soft-deleting employees.
It orchestrates domain services and repositories to execute the use case.

Architecture Rule: Delete is always soft - set is_active=False, never hard delete.
"""

import logging
from uuid import UUID

from apps.common.exceptions import EmployeeNotFoundException
from apps.employees.domain.ports.employee_port import EmployeePort
from apps.employees.domain.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)


class DeleteEmployeeCommand:
    """
    Use case: Soft delete an employee (set is_active=False).
    
    This command handler:
    1. Retrieves the existing employee
    2. Validates soft delete rules via EmployeeService
    3. Performs soft delete via repository
    """
    
    def __init__(self, repository: EmployeePort):
        """
        Initialize the command with a repository.
        
        Args:
            repository: EmployeePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, employee_id: UUID) -> bool:
        """
        Execute the delete employee use case.
        
        Args:
            employee_id: UUID of the employee to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            EmployeeNotFoundException: If employee doesn't exist
            ValueError: If validation fails
        """
        logger.info(f"Soft deleting employee with id: {employee_id}")
        
        try:
            # Retrieve existing employee
            existing = self.repository.get_by_id(employee_id)
            if not existing:
                raise EmployeeNotFoundException(f"Employee {employee_id} not found")
            
            # Validate soft delete
            EmployeeService.validate_soft_delete(existing)
            
            # Perform soft delete
            result = self.repository.soft_delete(employee_id)
            
            logger.info(f"Employee soft deleted successfully: {existing.employee_number}")
            return result
            
        except EmployeeNotFoundException as e:
            logger.warning(f"Employee deletion failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting employee: {str(e)}")
            raise