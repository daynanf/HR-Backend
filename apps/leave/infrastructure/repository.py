"""
Leave Request Repository Implementation

Implements the LeavePort interface using Django ORM.
This is the concrete implementation of the port defined in the domain layer.

Architecture Rule: Repositories implement port interfaces defined in the domain.
Views never call repositories directly - they go through the application layer.
"""

from typing import Optional, List, Dict
from uuid import UUID
from datetime import date, datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count

from apps.common.exceptions import (
    LeaveNotFoundException,
    LeaveOverlapException,
    InvalidLeaveStatusException,
)
from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.domain.ports.leave_port import LeavePort
from apps.leave.domain.services.leave_service import LeaveService
from apps.leave.infrastructure.models import LeaveRequestModel
from apps.leave.infrastructure.mappers import LeaveRequestMapper


class LeaveRepository(LeavePort):
    """
    Leave Repository - implements LeavePort using Django ORM.
    
    This repository handles all leave request persistence operations.
    It converts between ORM models and domain entities using the mapper.
    """
    
    def submit(self, leave: LeaveRequest) -> LeaveRequest:
        """
        Submit a new leave request.
        
        Args:
            leave: The LeaveRequest entity to persist
            
        Returns:
            LeaveRequest: The persisted leave request
            
        Raises:
            LeaveOverlapException: If the leave overlaps with an approved leave
            ValueError: If dates are invalid
        """
        with transaction.atomic():
            # Validate submission
            LeaveService.validate_submit({
                'leave_type': leave.leave_type,
                'employee_id': leave.employee_id,
                'start_date': leave.start_date,
                'end_date': leave.end_date,
            })
            
            # Validate dates
            LeaveService.validate_dates(leave.start_date, leave.end_date)
            
            # Check for overlaps
            existing_leaves = self.list_for_employee(leave.employee_id)
            LeaveService.check_overlap(
                leave.start_date,
                leave.end_date,
                existing_leaves
            )
            
            # Convert and save
            model_dict = LeaveRequestMapper.to_model_dict(leave)
            model = LeaveRequestModel.objects.create(**model_dict)
            
            return LeaveRequestMapper.to_entity(model)
    
    def get_by_id(self, id: UUID) -> Optional[LeaveRequest]:
        """
        Retrieve a leave request by UUID.
        
        Args:
            id: The leave request's UUID
            
        Returns:
            Optional[LeaveRequest]: The leave request if found, None otherwise
        """
        try:
            model = LeaveRequestModel.objects.select_related('employee').get(id=id)
            return LeaveRequestMapper.to_entity(model)
        except LeaveRequestModel.DoesNotExist:
            return None
    
    def list_for_employee(self, employee_id: UUID) -> List[LeaveRequest]:
        """
        List all leave requests for a specific employee.
        
        Args:
            employee_id: The employee's UUID
            
        Returns:
            List[LeaveRequest]: List of all leave requests for the employee
        """
        models = LeaveRequestModel.objects.filter(employee_id=employee_id)
        return [LeaveRequestMapper.to_entity(model) for model in models]
    
    def approve(self, id: UUID, reviewed_by: UUID) -> LeaveRequest:
        """
        Approve a pending leave request.
        
        Args:
            id: The leave request's UUID
            reviewed_by: The UUID of the employee who approved it
            
        Returns:
            LeaveRequest: The approved leave request
            
        Raises:
            LeaveNotFoundException: If the leave request doesn't exist
            InvalidLeaveStatusException: If the leave request is not PENDING
        """
        try:
            with transaction.atomic():
                model = LeaveRequestModel.objects.get(id=id)
                leave = LeaveRequestMapper.to_entity(model)
                
                # Validate status transition
                LeaveService.validate_status_transition(leave, 'approve')
                
                # Update the model
                model.status = 'APPROVED'
                model.reviewed_by_id = reviewed_by
                model.reviewed_at = timezone.now()
                model.save()
                
                return LeaveRequestMapper.to_entity(model)
                
        except LeaveRequestModel.DoesNotExist:
            raise LeaveNotFoundException(
                f"Leave request with id '{id}' not found"
            )
    
    def reject(self, id: UUID, reviewed_by: UUID) -> LeaveRequest:
        """
        Reject a pending leave request.
        
        Args:
            id: The leave request's UUID
            reviewed_by: The UUID of the employee who rejected it
            
        Returns:
            LeaveRequest: The rejected leave request
            
        Raises:
            LeaveNotFoundException: If the leave request doesn't exist
            InvalidLeaveStatusException: If the leave request is not PENDING
        """
        try:
            with transaction.atomic():
                model = LeaveRequestModel.objects.get(id=id)
                leave = LeaveRequestMapper.to_entity(model)
                
                # Validate status transition
                LeaveService.validate_status_transition(leave, 'reject')
                
                # Update the model
                model.status = 'REJECTED'
                model.reviewed_by_id = reviewed_by
                model.reviewed_at = timezone.now()
                model.save()
                
                return LeaveRequestMapper.to_entity(model)
                
        except LeaveRequestModel.DoesNotExist:
            raise LeaveNotFoundException(
                f"Leave request with id '{id}' not found"
            )
    
    def get_on_leave_count(self, as_of_date: date) -> int:
        """
        Count employees on approved leave as of a specific date.
        
        Args:
            as_of_date: The date to count on-leave employees
            
        Returns:
            int: Number of employees on approved leave on the given date
        """
        # Count approved leaves where the date falls between start and end
        count = LeaveRequestModel.objects.filter(
            status='APPROVED',
            start_date__lte=as_of_date,
            end_date__gte=as_of_date
        ).values('employee_id').distinct().count()
        
        return count
    
    def list_all(self, filters: Dict[str, str]) -> List[LeaveRequest]:
        """
        List all leave requests with optional filters.
        
        Args:
            filters: Dictionary of filter parameters
                - status: Filter by status (PENDING, APPROVED, REJECTED)
                - department: Filter by department code
                
        Returns:
            List[LeaveRequest]: List of leave requests matching the filters
        """
        qs = LeaveRequestModel.objects.select_related('employee', 'employee__department')
        
        # Apply status filter
        status = filters.get('status')
        if status and status.upper() in ['PENDING', 'APPROVED', 'REJECTED']:
            qs = qs.filter(status=status.upper())
        
        # Apply department filter
        department = filters.get('department')
        if department:
            qs = qs.filter(employee__department__code=department.upper())
        
        return [LeaveRequestMapper.to_entity(model) for model in qs]