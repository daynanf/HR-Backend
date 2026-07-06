"""
Create Department Command Handler

This is the application service for creating new departments.
It orchestrates domain services and repositories to execute the use case.
"""

import logging
from uuid import uuid4
from typing import Dict, Any

from apps.common.exceptions import DuplicateDepartmentCodeException
from apps.departments.domain.entities.department import Department
from apps.departments.domain.ports.department_port import DepartmentPort
from apps.departments.domain.services.department_service import DepartmentService

logger = logging.getLogger(__name__)


class CreateDepartmentCommand:
    """
    Use case: Create a new department with business rule validation.
    """
    
    def __init__(self, repository: DepartmentPort):
        self.repository = repository
    
    def execute(self, data: Dict[str, Any]) -> Department:
        """
        Execute the create department use case.
        
        Args:
            data: Dictionary containing department data:
                - code: str (unique, e.g., ENG)
                - name: str
                - description: Optional[str]
            
        Returns:
            Department: The created department entity
            
        Raises:
            DuplicateDepartmentCodeException: If code already exists
            ValueError: If validation fails
        """
        logger.info(f"Creating department with code: {data.get('code')}")
        
        try:
            # Check for duplicate code
            existing = self.repository.get_by_code(data['code'])
            if existing:
                raise DuplicateDepartmentCodeException(
                    f"Department code '{data['code']}' already exists"
                )
            
            # Validate via domain service
            DepartmentService.validate_create(data)
            
            # Create the department entity
            department = Department(
                id=uuid4(),
                code=data['code'].upper(),
                name=data['name'],
                description=data.get('description'),
                is_active=True,
            )
            
            # Persist via repository
            created = self.repository.create(department)
            
            logger.info(f"Department created successfully: {created.code}")
            return created
            
        except (DuplicateDepartmentCodeException, ValueError) as e:
            logger.warning(f"Department creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating department: {str(e)}")
            raise