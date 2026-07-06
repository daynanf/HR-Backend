"""
Department Domain Service

This service enforces all department business rules and invariants.
It operates purely on domain entities and knows nothing about databases or HTTP.

Architecture Rule: Domain services raise DomainException or ValueError,
never HTTP exceptions. The Presentation layer catches these and converts to HTTP responses.
"""

from typing import Dict, Any
from uuid import UUID

from apps.common.exceptions import DepartmentHasActiveEmployeesException


class DepartmentService:
    """
    Department domain service - enforces all department business rules.
    
    This service validates department operations and business rules.
    """
    
    @staticmethod
    def validate_deactivation(
        department_id: UUID,
        active_employee_count: int
    ) -> None:
        """
        Validate that a department can be deactivated.
        
        Business Rule:
        - A department cannot be deactivated if it has active employees
        
        Args:
            department_id: The UUID of the department to deactivate
            active_employee_count: Number of active employees in the department
            
        Raises:
            DepartmentHasActiveEmployeesException: If the department has active employees
        """
        if active_employee_count > 0:
            raise DepartmentHasActiveEmployeesException(
                f"Cannot deactivate department: {active_employee_count} active employees found. "
                f"Please reassign or deactivate all employees in this department first."
            )
    
    @staticmethod
    def validate_create(department_data: Dict[str, Any]) -> None:
        """
        Validate department creation data.
        
        Business Rules:
        1. Code must not be empty
        2. Name must not be empty
        3. Code must be alphanumeric
        
        Args:
            department_data: Dictionary containing department creation data
            
        Raises:
            ValueError: If any validation rule is violated
        """
        code = department_data.get('code')
        if not code or not code.strip():
            raise ValueError("code cannot be empty")
        
        name = department_data.get('name')
        if not name or not name.strip():
            raise ValueError("name cannot be empty")
        
        # Code should be uppercase alphanumeric
        if not code.isalnum():
            raise ValueError("code must be alphanumeric (letters and numbers only)")
        
        # Code should be uppercase (convert in infrastructure, but validate format)
        if code != code.upper():
            # We'll allow lowercase but standardize to uppercase in the repository
            # The validator just checks it's alphanumeric
            pass
    
    @staticmethod
    def validate_update(
        code: str,
        existing_code: str = None
    ) -> None:
        """
        Validate department update data.
        
        Business Rules:
        1. Code must be alphanumeric
        2. Code cannot be empty
        
        Args:
            code: The department code
            existing_code: The existing department code (for duplicate check)
            
        Raises:
            ValueError: If any validation rule is violated
        """
        if not code or not code.strip():
            raise ValueError("code cannot be empty")
        
        if not code.isalnum():
            raise ValueError("code must be alphanumeric (letters and numbers only)")