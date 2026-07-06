"""
Department Serializers

DRF serializers for Department entities.
These handle input validation and output formatting.
"""

from rest_framework import serializers
from uuid import UUID

from apps.departments.domain.entities.department import Department
from apps.departments.infrastructure.repository import DepartmentRepository


class DepartmentSerializer(serializers.Serializer):
    """
    Serializer for Department entities.
    
    Used for both read and write operations.
    """
    
    id = serializers.UUIDField(read_only=True)
    code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_active = serializers.BooleanField(read_only=True)
    
    def create(self, validated_data):
        """
        Create a new department.
        
        Args:
            validated_data: Validated input data
            
        Returns:
            Department: Created department entity
        """
        from apps.departments.application.commands.create_department import CreateDepartmentCommand
        
        repository = DepartmentRepository()
        command = CreateDepartmentCommand(repository)
        return command.execute(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update an existing department.
        
        Args:
            instance: The department entity to update (unused, we use validated_data)
            validated_data: Validated input data
            
        Returns:
            Department: Updated department entity
        """
        from apps.departments.application.commands.update_department import UpdateDepartmentCommand
        
        repository = DepartmentRepository()
        command = UpdateDepartmentCommand(repository)
        return command.execute(instance.id, validated_data)