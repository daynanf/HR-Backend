"""
Leave Request ORM Model

This is the Django ORM model for LeaveRequest persistence.
It is NOT the domain entity - it's the database representation.

Architecture Rule: Infrastructure models are for persistence only.
Domain entities are pure Python dataclasses.
"""

import uuid
from django.db import models
from django.core.validators import MinLengthValidator


class LeaveRequestModel(models.Model):
    """
    Django ORM model for Leave Request.
    
    This is the database representation of a leave request.
    Use LeaveRequestMapper to convert between this and the domain entity.
    """
    
    # Leave type choices
    class LeaveType(models.TextChoices):
        ANNUAL = 'ANNUAL', 'Annual Leave'
        SICK = 'SICK', 'Sick Leave'
        UNPAID = 'UNPAID', 'Unpaid Leave'
        MATERNITY = 'MATERNITY', 'Maternity Leave'
    
    # Status choices
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the leave request"
    )
    employee = models.ForeignKey(
        'employees.EmployeeModel',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        help_text="Reference to Employee"
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        help_text="Type of leave: ANNUAL, SICK, UNPAID, or MATERNITY"
    )
    start_date = models.DateField(
        db_index=True,
        help_text="Start date of the leave"
    )
    end_date = models.DateField(
        db_index=True,
        help_text="End date of the leave"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text="Status: PENDING, APPROVED, or REJECTED"
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Optional reason for the leave"
    )
    reviewed_by = models.ForeignKey(
        'employees.EmployeeModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves',
        help_text="Employee who reviewed this request (set on approve/reject)"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time the request was reviewed (set on approve/reject)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Auto-set on creation"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Auto-updated on save"
    )
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_number} - {self.leave_type} ({self.status})"