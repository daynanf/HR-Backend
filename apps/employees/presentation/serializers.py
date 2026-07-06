"""
Employee Serializers

DRF serializers for Employee entities.
These handle input validation and output formatting.
"""

from rest_framework import serializers
from uuid import UUID

from apps.employees.domain.entities.employee import Employee
from apps.employees.infrastructure.repository import EmployeeRepository
from apps.departments.infrastructure.repository import DepartmentRepository


class DepartmentNestedSerializer(serializers.Serializer):
    """
    Nested department object in employee responses.
    
    This is used to embed department details in employee responses.
    """
    
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()


class EmployeeSerializer(serializers.Serializer):
    """
    Read serializer - converts domain entity to JSON response.
    """
    
    id = serializers.UUIDField(read_only=True)
    employee_number = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department = DepartmentNestedSerializer(read_only=True)
    job_title = serializers.CharField()
    employment_type = serializers.ChoiceField(
        choices=['FULL_TIME', 'PART_TIME', 'CONTRACT']
    )
    hire_date = serializers.DateField()
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """
        Custom representation to include nested department object.
        
        Args:
            instance: Employee domain entity
            
        Returns:
            dict: Serialized data with nested department
        """
        data = super().to_representation(instance)
        
        # Add nested department data
        if hasattr(instance, 'department_id') and instance.department_id:
            repository = DepartmentRepository()
            department = repository.get_by_id(instance.department_id)
            if department:
                data['department'] = {
                    'id': str(department.id),
                    'code': department.code,
                    'name': department.name,
                    'is_active': department.is_active,
                }
        
        return data


class EmployeeCreateSerializer(serializers.Serializer):
    """
    Write serializer - validates input for create operations.
    """
    
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department_id = serializers.UUIDField()
    job_title = serializers.CharField(max_length=100)
    employment_type = serializers.ChoiceField(
        choices=['FULL_TIME', 'PART_TIME', 'CONTRACT']
    )
    hire_date = serializers.DateField()
    employee_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="Optional - auto-generated if not provided"
    )


class EmployeeUpdateSerializer(serializers.Serializer):
    """
    Write serializer - validates input for update operations.
    """
    
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department_id = serializers.UUIDField(required=False)
    job_title = serializers.CharField(max_length=100, required=False)
    employment_type = serializers.ChoiceField(
        choices=['FULL_TIME', 'PART_TIME', 'CONTRACT'],
        required=False
    )
    hire_date = serializers.DateField(required=False)
    is_active = serializers.BooleanField(required=False)


class BulkDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk delete operations.
    """
    
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of employee UUIDs to deactivate"
    )