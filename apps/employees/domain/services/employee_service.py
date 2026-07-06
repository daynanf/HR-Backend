"""
Employee Domain Service

This service enforces all employee business rules and invariants.
It operates purely on domain entities and knows nothing about databases or HTTP.

Architecture Rule: Domain services raise DomainException or ValueError,
never HTTP exceptions. The Presentation layer catches these and converts to HTTP responses.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from apps.common.exceptions import (
    DuplicateEmailException,
    DuplicateEmployeeNumberException,
    InvalidEmploymentTypeException,
)
from apps.employees.domain.entities.employee import Employee


class EmployeeService:
    """
    Employee domain service - enforces all employee business rules.
    
    This service validates employee creation, updates, and other business operations.
    All validation is pure business logic with no external dependencies.
    """
    
    VALID_EMPLOYMENT_TYPES = ['FULL_TIME', 'PART_TIME', 'CONTRACT']
    
    @staticmethod
    def validate_create(
        employee_data: Dict[str, Any],
        existing_email: Optional[str] = None,
        existing_employee_number: Optional[str] = None
    ) -> None:
        """
        Validate employee creation data against business rules.
        
        Business Rules:
        1. Email must be unique across all employees
        2. Employee number must be unique across all employees
        3. Employment type must be valid (FULL_TIME, PART_TIME, CONTRACT)
        4. First name, last name, and email cannot be empty
        
        Args:
            employee_data: Dictionary containing employee creation data
            existing_email: Email of existing employee (if found)
            existing_employee_number: Employee number of existing employee (if found)
            
        Raises:
            DuplicateEmailException: If email is already in use
            DuplicateEmployeeNumberException: If employee number is already in use
            ValueError: If any validation rule is violated
        """
        # Check for duplicate email
        email = employee_data.get('email')
        if existing_email and email:
            raise DuplicateEmailException(
                f"Email '{email}' is already in use by another employee"
            )
        
        # Check for duplicate employee number
        employee_number = employee_data.get('employee_number')
        if existing_employee_number and employee_number:
            raise DuplicateEmployeeNumberException(
                f"Employee number '{employee_number}' is already in use"
            )
        
        # Validate employment type
        employment_type = employee_data.get('employment_type')
        if employment_type and employment_type not in EmployeeService.VALID_EMPLOYMENT_TYPES:
            raise InvalidEmploymentTypeException(
                f"employment_type must be one of: {', '.join(EmployeeService.VALID_EMPLOYMENT_TYPES)}"
            )
        
        # Validate required fields
        if not employee_data.get('first_name') or not employee_data.get('first_name').strip():
            raise ValueError("first_name cannot be empty")
        
        if not employee_data.get('last_name') or not employee_data.get('last_name').strip():
            raise ValueError("last_name cannot be empty")
        
        if not employee_data.get('email') or '@' not in employee_data.get('email', ''):
            raise ValueError("Invalid email address")
    
    @staticmethod
    def validate_update(
        employee: Employee,
        update_data: Dict[str, Any],
        conflicting_email: Optional[str] = None
    ) -> None:
        """
        Validate employee update data against business rules.
        
        Business Rules:
        1. Email must be unique across all employees (except the current employee)
        2. Employment type must be valid
        3. Cannot update with empty required fields
        
        Args:
            employee: The existing Employee entity being updated
            update_data: Dictionary containing update data
            conflicting_email: Email of another employee with the same email (if found)
            
        Raises:
            DuplicateEmailException: If email is already in use by another employee
            ValueError: If any validation rule is violated
        """
        # Check for duplicate email (exclude current employee)
        new_email = update_data.get('email')
        if new_email and conflicting_email and conflicting_email != employee.email:
            raise DuplicateEmailException(
                f"Email '{new_email}' is already in use by another employee"
            )
        
        # Validate employment type if provided
        employment_type = update_data.get('employment_type')
        if employment_type and employment_type not in EmployeeService.VALID_EMPLOYMENT_TYPES:
            raise InvalidEmploymentTypeException(
                f"employment_type must be one of: {', '.join(EmployeeService.VALID_EMPLOYMENT_TYPES)}"
            )
        
        # Validate required fields if they are being updated
        if 'first_name' in update_data:
            if not update_data['first_name'] or not update_data['first_name'].strip():
                raise ValueError("first_name cannot be empty")
        
        if 'last_name' in update_data:
            if not update_data['last_name'] or not update_data['last_name'].strip():
                raise ValueError("last_name cannot be empty")
        
        if 'email' in update_data:
            if not update_data['email'] or '@' not in update_data['email']:
                raise ValueError("Invalid email address")
    
    @staticmethod
    def validate_soft_delete(employee: Employee) -> None:
        """
        Validate that an employee can be soft-deleted.
        
        Business Rules:
        1. Employee must exist (checked by caller)
        2. No additional rules currently, but this validates any future rules
        
        Args:
            employee: The Employee entity to soft delete
            
        Raises:
            ValueError: If the employee is already inactive
        """
        if not employee.is_active:
            raise ValueError(f"Employee {employee.employee_number} is already inactive")
    
    @staticmethod
    def is_active_employee(employee: Employee) -> bool:
        """
        Check if an employee is active.
        
        Args:
            employee: The Employee entity
            
        Returns:
            bool: True if the employee is active
        """
        return employee.is_active
    
    @staticmethod
    def get_full_name(employee: Employee) -> str:
        """
        Get the employee's full name.
        
        Args:
            employee: The Employee entity
            
        Returns:
            str: The full name (first_name + last_name)
        """
        return employee.get_full_name()