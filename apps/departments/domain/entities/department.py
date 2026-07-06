"""
Department Domain Entity

This is a plain Python dataclass with NO Django or DRF imports.
It represents the business concept of a Department in the HR system.

Architecture Rule: Domain entities MUST NOT import from django or rest_framework.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Department:
    """
    Department domain entity - pure business object.
    
    This represents a department in the HR system.
    No ORM, no database, no HTTP - just business data and rules.
    
    Attributes:
        id: Unique identifier (UUID)
        code: Unique department code (e.g., ENG for Engineering)
        name: Department name
        description: Optional description
        is_active: Whether the department is active
    """
    id: UUID = field(default_factory=uuid4)
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    
    def __post_init__(self):
        """
        Validate business rules after initialization.
        
        Raises:
            ValueError: If any validation rule is violated.
        """
        if not self.code or not self.code.strip():
            raise ValueError("code cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        
        # Code should be uppercase and alphanumeric
        if not self.code.isalnum():
            raise ValueError("code must be alphanumeric")
    
    def get_display_name(self) -> str:
        """Get the display name (code - name)."""
        return f"{self.code} - {self.name}"