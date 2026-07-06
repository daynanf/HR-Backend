"""
Leave Request Serializers

DRF serializers for LeaveRequest entities.
"""

from rest_framework import serializers
from uuid import UUID

from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.infrastructure.repository import LeaveRepository


class LeaveRequestSerializer(serializers.Serializer):
    """
    Serializer for LeaveRequest entities.
    """
    
    id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField()
    leave_type = serializers.ChoiceField(
        choices=['ANNUAL', 'SICK', 'UNPAID', 'MATERNITY']
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.ChoiceField(
        choices=['PENDING', 'APPROVED', 'REJECTED'],
        read_only=True
    )
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    reviewed_by = serializers.UUIDField(read_only=True, allow_null=True)
    reviewed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def create(self, validated_data):
        """
        Create a new leave request.
        """
        from apps.leave.application.commands.submit_leave import SubmitLeaveCommand
        
        repository = LeaveRepository()
        command = SubmitLeaveCommand(repository)
        return command.execute(validated_data)


class LeaveSubmitSerializer(serializers.Serializer):
    """
    Serializer for submitting leave requests.
    """
    
    employee_id = serializers.UUIDField()
    leave_type = serializers.ChoiceField(
        choices=['ANNUAL', 'SICK', 'UNPAID', 'MATERNITY']
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    def validate(self, data):
        """
        Custom validation for leave dates.
        """
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError(
                "end_date must be greater than or equal to start_date"
            )
        return data


class LeaveUpdateStatusSerializer(serializers.Serializer):
    """
    Serializer for approve/reject operations.
    """
    
    reviewed_by = serializers.UUIDField(required=False)