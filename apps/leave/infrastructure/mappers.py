"""
Leave Request Mapper

Handles conversion between ORM model and domain entity.
This ensures the domain layer knows nothing about the database.

Architecture Rule: Mappers handle ALL ORM <-> entity conversion.
No raw ORM access in domain layer.
"""

from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.infrastructure.models import LeaveRequestModel


class LeaveRequestMapper:
    """
    Mapper for LeaveRequest - converts between ORM model and domain entity.
    
    Direction: Database (ORM) <-> Domain Entity
    """
    
    @staticmethod
    def to_entity(model: LeaveRequestModel) -> LeaveRequest:
        """
        Convert ORM model to domain entity.
        
        Called after every database read.
        
        Args:
            model: LeaveRequestModel instance from Django ORM
            
        Returns:
            LeaveRequest: Domain entity (pure Python dataclass)
        """
        return LeaveRequest(
            id=model.id,
            employee_id=model.employee_id,
            leave_type=model.leave_type,
            start_date=model.start_date,
            end_date=model.end_date,
            status=model.status,
            reason=model.reason,
            reviewed_by=model.reviewed_by_id,
            reviewed_at=model.reviewed_at,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model_dict(entity: LeaveRequest, employee_id=None) -> dict:
        """
        Convert domain entity to dict for ORM create/update.
        
        Called before database writes.
        
        Args:
            entity: LeaveRequest domain entity
            employee_id: Employee ID (can come from entity or be passed separately)
            
        Returns:
            dict: Dictionary for ORM create/update
        """
        return {
            'id': entity.id,
            'employee_id': employee_id or entity.employee_id,
            'leave_type': entity.leave_type,
            'start_date': entity.start_date,
            'end_date': entity.end_date,
            'status': entity.status,
            'reason': entity.reason,
            'reviewed_by_id': entity.reviewed_by,
            'reviewed_at': entity.reviewed_at,
        }
    
    @staticmethod
    def to_model_update_dict(entity: LeaveRequest) -> dict:
        """
        Convert domain entity to dict for ORM update only.
        
        Excludes fields that shouldn't be updated directly.
        
        Args:
            entity: LeaveRequest domain entity
            
        Returns:
            dict: Dictionary for ORM update
        """
        return {
            'leave_type': entity.leave_type,
            'start_date': entity.start_date,
            'end_date': entity.end_date,
            'status': entity.status,
            'reason': entity.reason,
            'reviewed_by_id': entity.reviewed_by,
            'reviewed_at': entity.reviewed_at,
        }