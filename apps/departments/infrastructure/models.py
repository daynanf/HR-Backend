"""
Department ORM Model

This is the Django ORM model for Department persistence.
It is NOT the domain entity - it's the database representation.

Architecture Rule: Infrastructure models are for persistence only.
Domain entities are pure Python dataclasses.
"""

import uuid
from django.db import models


class DepartmentModel(models.Model):
    """
    Django ORM model for Department.
    
    This is the database representation of a department.
    Use DepartmentMapper to convert between this and the domain entity.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the department"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Unique department code (e.g., ENG for Engineering)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Department name"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the department"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the department is active (soft delete)"
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
        db_table = 'departments'
        ordering = ['code']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"