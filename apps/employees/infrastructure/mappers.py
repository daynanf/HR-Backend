"""
Employee Mapper

Handles conversion between ORM model and domain entity.
This ensures the domain layer knows nothing about the database.

Architecture Rule: Mappers handle ALL ORM <-> entity conversion.
No raw ORM access in domain layer.
"""

from apps.employees.domain.entities.employee import Employee
from apps.employees.infrastructure.models import EmployeeModel
from apps.departments.infrastructure.mappers import DepartmentMapper


class EmployeeMapper:
    """
    Mapper for Employee - converts between ORM model and domain entity.
    
    Direction: Database (ORM) <-> Domain Entity
    """
    
    @staticmethod
    def to_entity(model: EmployeeModel) -> Employee:
        """
        Convert ORM model to domain entity.
        
        Called after every database read.
        
        Args:
            model: EmployeeModel instance from Django ORM
            
        Returns:
            Employee: Domain entity (pure Python dataclass)
        """
        return Employee(
            employee_number=model.employee_number,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            job_title=model.job_title,
            employment_type=model.employment_type,
            hire_date=model.hire_date,
            
            # optional fields
            
            id=model.id,
            phone=model.phone,
            department_id=model.department_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model_dict(entity: Employee, department_model=None) -> dict:
        """
        Convert domain entity to dict for ORM create/update.
        
        Called before database writes.
        
        Args:
            entity: Employee domain entity
            department_model: Optional department model instance (for efficiency)
            
        Returns:
            dict: Dictionary for ORM create/update
        """
        return {            
            'employee_number': entity.employee_number,
            'first_name': entity.first_name,
            'last_name': entity.last_name,
            'email': entity.email,            
            'job_title': entity.job_title,
            'employment_type': entity.employment_type,
            'hire_date': entity.hire_date,
            'id': entity.id,
            'phone': entity.phone,
            'department_id': entity.department_id,
            'is_active': entity.is_active,
        }
    
    @staticmethod
    def to_model_update_dict(entity: Employee) -> dict:
        """
        Convert domain entity to dict for ORM update only.
        
        Excludes fields that shouldn't be updated directly.
        
        Args:
            entity: Employee domain entity
            
        Returns:
            dict: Dictionary for ORM update
        """
        return {
            'employee_number': entity.employee_number,
            'first_name': entity.first_name,
            'last_name': entity.last_name,
            'email': entity.email,
            'phone': entity.phone,
            'department_id': entity.department_id,
            'job_title': entity.job_title,
            'employment_type': entity.employment_type,
            'hire_date': entity.hire_date,
            'is_active': entity.is_active,
        }