"""
Department Repository Implementation

Implements the DepartmentPort interface using Django ORM.
This is the concrete implementation of the port defined in the domain layer.

Architecture Rule: Repositories implement port interfaces defined in the domain.
Views never call repositories directly - they go through the application layer.
"""

from typing import Optional, List
from uuid import UUID
from django.db import IntegrityError, transaction
from django.db.models import Count

from apps.common.exceptions import (
    DepartmentNotFoundException,
    DuplicateDepartmentCodeException,
    DepartmentHasActiveEmployeesException,
)
from apps.departments.domain.entities.department import Department
from apps.departments.domain.ports.department_port import DepartmentPort
from apps.departments.domain.services.department_service import DepartmentService
from apps.departments.infrastructure.models import DepartmentModel
from apps.departments.infrastructure.mappers import DepartmentMapper


class DepartmentRepository(DepartmentPort):
    """
    Department Repository - implements DepartmentPort using Django ORM.
    
    This repository handles all department persistence operations.
    It converts between ORM models and domain entities using the mapper.
    """
    
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
        try:
            with transaction.atomic():
                # Validate creation
                DepartmentService.validate_create({
                    'code': department.code,
                    'name': department.name,
                })
                
                # Convert and save
                model_dict = DepartmentMapper.to_model_dict(department)
                model = DepartmentModel.objects.create(**model_dict)
                
                return DepartmentMapper.to_entity(model)
                
        except IntegrityError as e:
            if 'code' in str(e).lower():
                raise DuplicateDepartmentCodeException(
                    f"Department code '{department.code}' already exists"
                )
            raise
    
    def get_by_id(self, id: UUID) -> Optional[Department]:
        """
        Retrieve a department by UUID.
        
        Args:
            id: The department's UUID
            
        Returns:
            Optional[Department]: The department if found, None otherwise
        """
        try:
            model = DepartmentModel.objects.get(id=id)
            return DepartmentMapper.to_entity(model)
        except DepartmentModel.DoesNotExist:
            return None
    
    def get_by_code(self, code: str) -> Optional[Department]:
        """
        Retrieve a department by code.
        
        Args:
            code: The department's code (e.g., ENG)
            
        Returns:
            Optional[Department]: The department if found, None otherwise
        """
        try:
            model = DepartmentModel.objects.get(code=code.upper())
            return DepartmentMapper.to_entity(model)
        except DepartmentModel.DoesNotExist:
            return None
    
    def list_all(self) -> List[Department]:
        """
        List all departments.
        
        Returns:
            List[Department]: List of all departments
        """
        models = DepartmentModel.objects.all()
        return [DepartmentMapper.to_entity(model) for model in models]
    
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
        try:
            with transaction.atomic():
                # Check if department exists
                existing = DepartmentModel.objects.get(id=department.id)
                
                # Check for duplicate code
                if existing.code != department.code:
                    if DepartmentModel.objects.filter(code=department.code.upper()).exists():
                        raise DuplicateDepartmentCodeException(
                            f"Department code '{department.code}' already exists"
                        )
                
                # Update the model
                model_dict = DepartmentMapper.to_model_dict(department)
                for key, value in model_dict.items():
                    setattr(existing, key, value)
                existing.save()
                
                return DepartmentMapper.to_entity(existing)
                
        except DepartmentModel.DoesNotExist:
            raise DepartmentNotFoundException(
                f"Department with id '{department.id}' not found"
            )
    
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
        try:
            with transaction.atomic():
                model = DepartmentModel.objects.get(id=id)
                
                # Check if department has active employees
                active_employee_count = model.employees.filter(is_active=True).count()
                DepartmentService.validate_deactivation(id, active_employee_count)
                
                model.is_active = False
                model.save()
                return True
                
        except DepartmentModel.DoesNotExist:
            raise DepartmentNotFoundException(
                f"Department with id '{id}' not found"
            )
    
    def get_active_employee_count(self, department_id: UUID) -> int:
        """
        Count active employees in a department.
        
        Args:
            department_id: The department's UUID
            
        Returns:
            int: Number of active employees in the department
        """
        try:
            model = DepartmentModel.objects.get(id=department_id)
            return model.employees.filter(is_active=True).count()
        except DepartmentModel.DoesNotExist:
            return 0