"""
Employee Port Interface

This defines the contract between the Application layer and the Infrastructure layer.
The infrastructure layer implements this interface using Django ORM.

Architecture Rule: Port interfaces are abstract base classes defined in the domain layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from uuid import UUID

from apps.employees.domain.entities.employee import Employee


class EmployeePort(ABC):
    """
    Interface for Employee Repository operations.
    
    This port defines WHAT operations are available, not HOW they are implemented.
    The infrastructure layer provides concrete implementations.
    """
    
    @abstractmethod
    def create(self, employee: Employee) -> Employee:
        """
        Persist a new employee.
        
        Args:
            employee: The Employee entity to persist
            
        Returns:
            Employee: The persisted employee with any auto-generated fields filled
            
        Raises:
            DuplicateEmailException: If email already exists
            DuplicateEmployeeNumberException: If employee number already exists
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Employee]:
        """
        Retrieve an employee by UUID.
        
        Args:
            id: The employee's UUID
            
        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Retrieve an employee by email address.
        
        Args:
            email: The employee's email address
            
        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        """
        Retrieve an employee by employee number.
        
        Args:
            employee_number: The employee's unique number (e.g., EMP-001)
            
        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_active(self, filters: Dict[str, str]) -> List[Employee]:
        """
        List all active employees with optional filters.
        
        Args:
            filters: Dictionary of filter parameters
                - search: Search by first_name or last_name
                - department: Filter by department code
                
        Returns:
            List[Employee]: List of active employees matching the filters
        """
        pass
    
    @abstractmethod
    def update(self, employee: Employee) -> Employee:
        """
        Update an existing employee.
        
        Args:
            employee: The Employee entity with updated fields
            
        Returns:
            Employee: The updated employee
            
        Raises:
            EmployeeNotFoundException: If the employee doesn't exist
            DuplicateEmailException: If email already exists for another employee
        """
        pass
    
    @abstractmethod
    def soft_delete(self, id: UUID) -> bool:
        """
        Soft delete an employee (set is_active=False).
        
        This is a soft delete - the record remains in the database
        but is excluded from active lists.
        
        Args:
            id: The employee's UUID
            
        Returns:
            bool: True if deleted, False if employee not found
            
        Raises:
            EmployeeNotFoundException: If the employee doesn't exist
        """
        pass
    
    @abstractmethod
    def bulk_deactivate(self, ids: List[UUID]) -> Dict[str, int]:
        """
        Deactivate multiple employees.
        
        Args:
            ids: List of employee UUIDs to deactivate
            
        Returns:
            Dict[str, int]: Dictionary with counts:
                - deactivated: Number successfully deactivated
                - already_inactive: Number already inactive
                - not_found: Number not found
        """
        pass
    
    @abstractmethod
    def get_next_employee_number(self) -> str:
        """
        Generate the next employee number.
        
        Format: EMP-001, EMP-002, EMP-003, ...
        
        Returns:
            str: The next available employee number
        """
        pass