"""
Department Port Interface

This defines the contract between the Application layer and the Infrastructure layer.
The infrastructure layer implements this interface using Django ORM.

Architecture Rule: Port interfaces are abstract base classes defined in the domain layer.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from apps.departments.domain.entities.department import Department


class DepartmentPort(ABC):
    """
    Interface for Department Repository operations.
    """
    
    @abstractmethod
    def create(self, department: Department) -> Department:
        """
        Persist a new department.
        
        Args:
            department: The Department entity to persist
            
        Returns:
            Department: The persisted department
            
        Raises:
            DuplicateDepartmentCodeException: If code already exists
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Department]:
        """
        Retrieve a department by UUID.
        
        Args:
            id: The department's UUID
            
        Returns:
            Optional[Department]: The department if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Department]:
        """
        Retrieve a department by code.
        
        Args:
            code: The department's code (e.g., ENG)
            
        Returns:
            Optional[Department]: The department if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_all(self) -> List[Department]:
        """
        List all departments.
        
        Returns:
            List[Department]: List of all departments
        """
        pass
    
    @abstractmethod
    def update(self, department: Department) -> Department:
        """
        Update an existing department.
        
        Args:
            department: The Department entity with updated fields
            
        Returns:
            Department: The updated department
            
        Raises:
            DepartmentNotFoundException: If the department doesn't exist
            DuplicateDepartmentCodeException: If code already exists for another department
        """
        pass
    
    @abstractmethod
    def deactivate(self, id: UUID) -> bool:
        """
        Deactivate a department (set is_active=False).
        
        Args:
            id: The department's UUID
            
        Returns:
            bool: True if deactivated
            
        Raises:
            DepartmentNotFoundException: If the department doesn't exist
            DepartmentHasActiveEmployeesException: If the department has active employees
        """
        pass
    
    @abstractmethod
    def get_active_employee_count(self, department_id: UUID) -> int:
        """
        Count active employees in a department.
        
        Args:
            department_id: The department's UUID
            
        Returns:
            int: Number of active employees in the department
        """
        pass