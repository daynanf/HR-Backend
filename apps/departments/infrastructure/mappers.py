"""
Department Mapper

Handles conversion between ORM model and domain entity.
This ensures the domain layer knows nothing about the database.

Architecture Rule: Mappers handle ALL ORM <-> entity conversion.
No raw ORM access in domain layer.
"""

from apps.departments.domain.entities.department import Department
from apps.departments.infrastructure.models import DepartmentModel


class DepartmentMapper:
    """
    Mapper for Department - converts between ORM model and domain entity.
    
    Direction: Database (ORM) <-> Domain Entity
    """
    
    @staticmethod
    def to_entity(model: DepartmentModel) -> Department:
        """
        Convert ORM model to domain entity.
        
        Called after every database read.
        
        Args:
            model: DepartmentModel instance from Django ORM
            
        Returns:
            Department: Domain entity (pure Python dataclass)
        """
        return Department(
            id=model.id,
            code=model.code,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
        )
    
    @staticmethod
    def to_model_dict(entity: Department) -> dict:
        """
        Convert domain entity to dict for ORM create/update.
        
        Called before database writes.
        
        Args:
            entity: Department domain entity
            
        Returns:
            dict: Dictionary for ORM create/update
        """
        return {
            'id': entity.id,
            'code': entity.code.upper(),  # Standardize to uppercase
            'name': entity.name,
            'description': entity.description,
            'is_active': entity.is_active,
        }