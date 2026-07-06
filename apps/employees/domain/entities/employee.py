"""
Employee Domain Entity

This is a plain Python dataclass with NO Django or DRF imports.
It represents the business concept of an Employee in the HR system.

Architecture Rule: Domain entities MUST NOT import from django or rest_framework.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Employee:
    """
    Employee domain entity - pure business object.
    
    This represents an employee in the HR system with all business attributes.
    No ORM, no database, no HTTP - just business data and rules.
    
    Attributes:
        id: Unique identifier (UUID)
        employee_number: Unique employee identifier (e.g., EMP-001)
        first_name: Employee's first name
        last_name: Employee's last name
        email: Unique email address
        phone: Optional phone number
        department_id: Reference to Department entity (by ID)
        job_title: Employee's job title
        employment_type: FULL_TIME, PART_TIME, or CONTRACT
        hire_date: Date the employee was hired
        is_active: Whether the employee is active (soft delete)
        created_at: Auto-set on creation
        updated_at: Auto-updated on changes
    """
    id: UUID = field(default_factory=uuid4)
    employee_number: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department_id: UUID = None
    job_title: str
    employment_type: str  # FULL_TIME, PART_TIME, CONTRACT
    hire_date: date
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Validate business rules after initialization.
        
        Raises:
            ValueError: If any validation rule is violated.
        """
        # Employment type validation
        valid_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT']
        if self.employment_type not in valid_types:
            raise ValueError(
                f"employment_type must be one of: {', '.join(valid_types)}"
            )
        
        # Name validation
        if not self.first_name or not self.first_name.strip():
            raise ValueError("first_name cannot be empty")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("last_name cannot be empty")
        
        # Email validation (basic)
        if not self.email or '@' not in self.email:
            raise ValueError("Invalid email address")
        
        # Employee number validation
        if not self.employee_number or not self.employee_number.strip():
            raise ValueError("employee_number cannot be empty")
    
    def get_full_name(self) -> str:
        """Get the employee's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def is_contractor(self) -> bool:
        """Check if employee is a contractor."""
        return self.employment_type == 'CONTRACT'
    
    def is_part_time(self) -> bool:
        """Check if employee is part-time."""
        return self.employment_type == 'PART_TIME'
    
    def is_full_time(self) -> bool:
        """Check if employee is full-time."""
        return self.employment_type == 'FULL_TIME'