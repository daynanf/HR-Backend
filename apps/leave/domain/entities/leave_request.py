"""
LeaveRequest Domain Entity

This is a plain Python dataclass with NO Django or DRF imports.
It represents the business concept of a Leave Request in the HR system.

Architecture Rule: Domain entities MUST NOT import from django or rest_framework.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class LeaveRequest:
    """
    LeaveRequest domain entity - pure business object.
    
    This represents a leave request in the HR system.
    No ORM, no database, no HTTP - just business data and rules.
    
    Attributes:
        id: Unique identifier (UUID)
        employee_id: Reference to Employee entity
        leave_type: ANNUAL, SICK, UNPAID, or MATERNITY
        start_date: Start date of the leave
        end_date: End date of the leave
        status: PENDING, APPROVED, or REJECTED
        reason: Optional reason for the leave
        reviewed_by: ID of the employee who reviewed this request
        reviewed_at: Date and time the request was reviewed
        created_at: Auto-set on creation
    """
    employee_id: UUID
    leave_type: str  # ANNUAL, SICK, UNPAID, MATERNITY
    start_date: date
    end_date: date
    status: str = 'PENDING'  # PENDING, APPROVED, REJECTED
    id: UUID = field(default_factory=uuid4)
    reason: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Validate business rules after initialization.
        
        Raises:
            ValueError: If any validation rule is violated.
        """
        # Leave type validation
        valid_types = ['ANNUAL', 'SICK', 'UNPAID', 'MATERNITY']
        if self.leave_type not in valid_types:
            raise ValueError(
                f"leave_type must be one of: {', '.join(valid_types)}"
            )
        
        # Status validation
        valid_statuses = ['PENDING', 'APPROVED', 'REJECTED']
        if self.status not in valid_statuses:
            raise ValueError(
                f"status must be one of: {', '.join(valid_statuses)}"
            )
        
        # Date validation
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
    
    def is_approved(self) -> bool:
        """Check if the leave request is approved."""
        return self.status == 'APPROVED'
    
    def is_pending(self) -> bool:
        """Check if the leave request is pending."""
        return self.status == 'PENDING'
    
    def is_rejected(self) -> bool:
        """Check if the leave request is rejected."""
        return self.status == 'REJECTED'
    
    def get_duration_days(self) -> int:
        """Get the number of days requested (inclusive)."""
        return (self.end_date - self.start_date).days + 1