"""
Employee ORM Model

This is the Django ORM model for Employee persistence.
It is NOT the domain entity - it's the database representation.

Architecture Rule: Infrastructure models are for persistence only.
Domain entities are pure Python dataclasses.
"""

import uuid
from django.db import models
from django.core.validators import EmailValidator


class EmployeeModel(models.Model):
    """
    Django ORM model for Employee.
    
    This is the database representation of an employee.
    Use EmployeeMapper to convert between this and the domain entity.
    """
    
    # Employment type choices
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full Time'
        PART_TIME = 'PART_TIME', 'Part Time'
        CONTRACT = 'CONTRACT', 'Contract'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the employee"
    )
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique employee identifier (e.g., EMP-001)"
    )
    first_name = models.CharField(
        max_length=100,
        help_text="Employee's first name"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Employee's last name"
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        validators=[EmailValidator()],
        help_text="Unique email address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Optional phone number"
    )
    department = models.ForeignKey(
        'departments.DepartmentModel',
        on_delete=models.PROTECT,  # Prevent deletion if employees exist
        related_name='employees',
        help_text="Reference to Department"
    )
    job_title = models.CharField(
        max_length=100,
        help_text="Employee's job title"
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        help_text="Employment type: FULL_TIME, PART_TIME, or CONTRACT"
    )
    hire_date = models.DateField(
        help_text="Date the employee was hired"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether the employee is active (soft delete)"
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
        db_table = 'employees'
        ordering = ['employee_number']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        
        indexes = [
            models.Index(fields=['employee_number']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['first_name', 'last_name']),
        ]
    
    def __str__(self):
        return f"{self.employee_number} - {self.first_name} {self.last_name}"