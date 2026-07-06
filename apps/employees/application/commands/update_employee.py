"""
Update Employee Command Handler

This is the application service for updating existing employees.
It orchestrates domain services and repositories to execute the use case.

Architecture Rule: Command handlers orchestrate domain objects and ports.
They contain NO HTTP concerns and NO ORM access directly.
"""

import logging
from uuid import UUID
from typing import Dict, Any

from apps.common.exceptions import EmployeeNotFoundException, DuplicateEmailException
from apps.employees.domain.entities.employee import Employee
from apps.employees.domain.ports.employee_port import EmployeePort
from apps.employees.domain.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)


class UpdateEmployeeCommand:
    """
    Use case: Update an existing employee with business rule validation.
    
    This command handler:
    1. Retrieves the existing employee
    2. Checks for email conflicts
    3. Validates all business rules via EmployeeService
    4. Updates and persists the Employee entity
    """
    
    def __init__(self, repository: EmployeePort):
        """
        Initialize the command with a repository.
        
        Args:
            repository: EmployeePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, employee_id: UUID, data: Dict[str, Any]) -> Employee:
        """
        Execute the update employee use case.
        
        Args:
            employee_id: UUID of the employee to update
            data: Dictionary containing updated employee data
            
        Returns:
            Employee: The updated employee entity
            
        Raises:
            EmployeeNotFoundException: If employee doesn't exist
            DuplicateEmailException: If email already exists for another employee
            ValueError: If validation fails
        """
        logger.info(f"Updating employee with id: {employee_id}")
        
        try:
            # Retrieve existing employee
            existing = self.repository.get_by_id(employee_id)
            if not existing:
                raise EmployeeNotFoundException(f"Employee {employee_id} not found")
            
            # Check for email conflict (if email is being changed)
            conflicting_email = None
            new_email = data.get('email')
            if new_email and new_email != existing.email:
                conflicting = self.repository.get_by_email(new_email)
                if conflicting:
                    conflicting_email = conflicting.email
            
            # Validate via domain service
            EmployeeService.validate_update(existing, data, conflicting_email)
            
            # Create updated employee entity
            updated_data = {
                'id': existing.id,
                'employee_number': existing.employee_number,
                'first_name': data.get('first_name', existing.first_name),
                'last_name': data.get('last_name', existing.last_name),
                'email': data.get('email', existing.email),
                'phone': data.get('phone', existing.phone),
                'department_id': data.get('department_id', existing.department_id),
                'job_title': data.get('job_title', existing.job_title),
                'employment_type': data.get('employment_type', existing.employment_type),
                'hire_date': data.get('hire_date', existing.hire_date),
                'is_active': existing.is_active,
                'created_at': existing.created_at,
                'updated_at': existing.updated_at,
            }
            
            updated_employee = Employee(**updated_data)
            
            # Persist via repository
            saved = self.repository.update(updated_employee)
            
            logger.info(f"Employee updated successfully: {saved.employee_number}")
            return saved
            
        except (EmployeeNotFoundException, DuplicateEmailException) as e:
            logger.warning(f"Employee update failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating employee: {str(e)}")
            raise