"""
Update Department Command Handler

This is the application service for updating existing departments.
"""

import logging
from uuid import UUID
from typing import Dict, Any

from apps.common.exceptions import DepartmentNotFoundException, DuplicateDepartmentCodeException
from apps.departments.domain.entities.department import Department
from apps.departments.domain.ports.department_port import DepartmentPort
from apps.departments.domain.services.department_service import DepartmentService

logger = logging.getLogger(__name__)


class UpdateDepartmentCommand:
    """
    Use case: Update an existing department with business rule validation.
    """
    
    def __init__(self, repository: DepartmentPort):
        self.repository = repository
    
    def execute(self, department_id: UUID, data: Dict[str, Any]) -> Department:
        """
        Execute the update department use case.
        
        Args:
            department_id: UUID of the department to update
            data: Dictionary containing updated department data
            
        Returns:
            Department: The updated department entity
            
        Raises:
            DepartmentNotFoundException: If department doesn't exist
            DuplicateDepartmentCodeException: If code already exists
            ValueError: If validation fails
        """
        logger.info(f"Updating department with id: {department_id}")
        
        try:
            # Retrieve existing department
            existing = self.repository.get_by_id(department_id)
            if not existing:
                raise DepartmentNotFoundException(f"Department {department_id} not found")
            
            # Check for duplicate code if code is being changed
            new_code = data.get('code')
            if new_code and new_code.upper() != existing.code:
                if self.repository.get_by_code(new_code):
                    raise DuplicateDepartmentCodeException(
                        f"Department code '{new_code}' already exists"
                    )
            
            # Create updated department entity
            updated_data = {
                'id': existing.id,
                'code': data.get('code', existing.code).upper(),
                'name': data.get('name', existing.name),
                'description': data.get('description', existing.description),
                'is_active': existing.is_active,
            }
            
            updated_department = Department(**updated_data)
            
            # Persist via repository
            saved = self.repository.update(updated_department)
            
            logger.info(f"Department updated successfully: {saved.code}")
            return saved
            
        except (DepartmentNotFoundException, DuplicateDepartmentCodeException) as e:
            logger.warning(f"Department update failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating department: {str(e)}")
            raise