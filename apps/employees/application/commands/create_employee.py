"""
Create Employee Command Handler

This is the application service for creating new employees.
It orchestrates domain services and repositories to execute the use case.

Architecture Rule: Command handlers orchestrate domain objects and ports.
They contain NO HTTP concerns and NO ORM access directly.
"""

import logging
from uuid import uuid4
from typing import Dict, Any

from apps.common.exceptions import DuplicateEmailException, DuplicateEmployeeNumberException
from apps.employees.domain.entities.employee import Employee
from apps.employees.domain.ports.employee_port import EmployeePort
from apps.employees.domain.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)


class CreateEmployeeCommand:
    """
    Use case: Create a new employee with business rule validation.
    
    This command handler:
    1. Checks for duplicate email and employee number
    2. Validates all business rules via EmployeeService
    3. Creates and persists the Employee entity
    """
    
    def __init__(self, repository: EmployeePort):
        """
        Initialize the command with a repository.
        
        Args:
            repository: EmployeePort implementation (injected)
        """
        self.repository = repository
    
    def execute(self, data: Dict[str, Any]) -> Employee:
        """
        Execute the create employee use case.
        
        Args:
            data: Dictionary containing employee data:
                - first_name: str
                - last_name: str
                - email: str
                - department_id: UUID
                - job_title: str
                - employment_type: str (FULL_TIME, PART_TIME, CONTRACT)
                - hire_date: date
                - phone: Optional[str]
                - employee_number: Optional[str] (auto-generated if not provided)
            
        Returns:
            Employee: The created employee entity
            
        Raises:
            DuplicateEmailException: If email already exists
            DuplicateEmployeeNumberException: If employee number already exists
            ValueError: If validation fails
        """
        logger.info(f"Creating employee with email: {data.get('email')}")
        
        try:
            # Check for duplicate email
            existing_email = self.repository.get_by_email(data['email'])
            
            # Get or generate employee number
            employee_number = data.get('employee_number')
            if not employee_number:
                employee_number = self.repository.get_next_employee_number()
                logger.debug(f"Auto-generated employee number: {employee_number}")
            
            # Check for duplicate employee number
            existing_number = self.repository.get_by_employee_number(employee_number)
            
            # Validate via domain service
            EmployeeService.validate_create(
                data,
                existing_email.email if existing_email else None,
                existing_number.employee_number if existing_number else None
            )
            
            # Create the employee entity
            employee = Employee(
                id=uuid4(),
                employee_number=employee_number,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone'),
                department_id=data['department_id'],
                job_title=data['job_title'],
                employment_type=data['employment_type'],
                hire_date=data['hire_date'],
                is_active=True,
            )
            
            # Persist via repository
            created = self.repository.create(employee)
            
            logger.info(f"Employee created successfully: {created.employee_number}")
            return created
            
        except (DuplicateEmailException, DuplicateEmployeeNumberException) as e:
            logger.warning(f"Employee creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating employee: {str(e)}")
            raise