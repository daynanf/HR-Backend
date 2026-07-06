"""
Employee Repository Implementation

Implements the EmployeePort interface using Django ORM.
This is the concrete implementation of the port defined in the domain layer.

Architecture Rule: Repositories implement port interfaces defined in the domain.
Views never call repositories directly - they go through the application layer.
"""

from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from django.db import IntegrityError, transaction
from django.db.models import Q, Count

from apps.common.exceptions import (
    EmployeeNotFoundException,
    DuplicateEmailException,
    DuplicateEmployeeNumberException,
)
from apps.employees.domain.entities.employee import Employee
from apps.employees.domain.ports.employee_port import EmployeePort
from apps.employees.domain.services.employee_service import EmployeeService
from apps.employees.infrastructure.models import EmployeeModel
from apps.employees.infrastructure.mappers import EmployeeMapper


class EmployeeRepository(EmployeePort):
    """
    Employee Repository - implements EmployeePort using Django ORM.
    
    This repository handles all employee persistence operations.
    It converts between ORM models and domain entities using the mapper.
    """
    
    def create(self, employee: Employee) -> Employee:
        """
        Persist a new employee.
        
        Args:
            employee: The Employee entity to persist
            
        Returns:
            Employee: The persisted employee
            
        Raises:
            DuplicateEmailException: If email already exists
            DuplicateEmployeeNumberException: If employee number already exists
        """
        try:
            with transaction.atomic():
                # Validate creation
                EmployeeService.validate_create(
                    {
                        'email': employee.email,
                        'employee_number': employee.employee_number,
                        'employment_type': employee.employment_type,
                        'first_name': employee.first_name,
                        'last_name': employee.last_name,
                    }
                )
                
                # Convert and save
                model_dict = EmployeeMapper.to_model_dict(employee)
                model = EmployeeModel.objects.create(**model_dict)
                
                return EmployeeMapper.to_entity(model)
                
        except IntegrityError as e:
            if 'email' in str(e).lower():
                raise DuplicateEmailException(
                    f"Email '{employee.email}' is already in use"
                )
            if 'employee_number' in str(e).lower():
                raise DuplicateEmployeeNumberException(
                    f"Employee number '{employee.employee_number}' is already in use"
                )
            raise
    
    def get_by_id(self, id: UUID) -> Optional[Employee]:
        """
        Retrieve an employee by UUID.
        
        Args:
            id: The employee's UUID
            
        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        try:
            model = EmployeeModel.objects.select_related('department').get(id=id)
            return EmployeeMapper.to_entity(model)
        except EmployeeModel.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Retrieve an employee by email address.
        
        Args:
            email: The employee's email address
            
        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        try:
            model = EmployeeModel.objects.get(email=email)
            return EmployeeMapper.to_entity(model)
        except EmployeeModel.DoesNotExist:
            return None
    
    def get_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        """
        Retrieve an employee by employee number.
        
        Args:
            employee_number: The employee's unique number (e.g., EMP-001)
            
        Returns:
            Optional[Employee]: The employee if found, None otherwise
        """
        try:
            model = EmployeeModel.objects.get(employee_number=employee_number)
            return EmployeeMapper.to_entity(model)
        except EmployeeModel.DoesNotExist:
            return None
    
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
        # Start with active employees
        qs = EmployeeModel.objects.filter(is_active=True).select_related('department')
        
        # Apply search filter
        search = filters.get('search')
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search)
            )
        
        # Apply department filter
        department = filters.get('department')
        if department:
            qs = qs.filter(department__code=department.upper())
        
        # Convert to domain entities
        return [EmployeeMapper.to_entity(model) for model in qs]
    
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
        try:
            with transaction.atomic():
                # Get existing employee
                model = EmployeeModel.objects.select_related('department').get(id=employee.id)
                
                # Check for email conflict (only if email changed)
                if model.email != employee.email:
                    if EmployeeModel.objects.filter(email=employee.email).exists():
                        raise DuplicateEmailException(
                            f"Email '{employee.email}' is already in use by another employee"
                        )
                
                # Update the model
                update_dict = EmployeeMapper.to_model_update_dict(employee)
                for key, value in update_dict.items():
                    setattr(model, key, value)
                model.save()
                
                return EmployeeMapper.to_entity(model)
                
        except EmployeeModel.DoesNotExist:
            raise EmployeeNotFoundException(
                f"Employee with id '{employee.id}' not found"
            )
        except IntegrityError as e:
            if 'email' in str(e).lower():
                raise DuplicateEmailException(
                    f"Email '{employee.email}' is already in use"
                )
            raise
    
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
        try:
            with transaction.atomic():
                model = EmployeeModel.objects.get(id=id)
                
                # Validate soft delete
                employee = EmployeeMapper.to_entity(model)
                EmployeeService.validate_soft_delete(employee)
                
                model.is_active = False
                model.save()
                return True
                
        except EmployeeModel.DoesNotExist:
            raise EmployeeNotFoundException(
                f"Employee with id '{id}' not found"
            )
    
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
        result = {
            'deactivated': 0,
            'already_inactive': 0,
            'not_found': 0,
        }
        
        if not ids:
            return result
        
        # Get all employees in one query
        models = EmployeeModel.objects.filter(id__in=ids)
        model_ids = set(str(model.id) for model in models)
        requested_ids = set(str(id) for id in ids)
        
        # Find not found
        not_found_ids = requested_ids - model_ids
        result['not_found'] = len(not_found_ids)
        
        # Process found employees
        for model in models:
            if not model.is_active:
                result['already_inactive'] += 1
            else:
                model.is_active = False
                model.save()
                result['deactivated'] += 1
        
        return result
    
    def get_next_employee_number(self) -> str:
        """
        Generate the next employee number.
        
        Format: EMP-001, EMP-002, EMP-003, ...
        
        Returns:
            str: The next available employee number
        """
        # Get the latest employee number
        last_employee = EmployeeModel.objects.order_by('-employee_number').first()
        
        if not last_employee:
            return 'EMP-001'
        
        # Extract the number from EMP-XXX
        try:
            last_number = int(last_employee.employee_number.split('-')[1])
            next_number = last_number + 1
            return f"EMP-{next_number:03d}"
        except (IndexError, ValueError):
            # If the format is unexpected, just use count + 1
            count = EmployeeModel.objects.count()
            return f"EMP-{count + 1:03d}"