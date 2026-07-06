# Domain layer for Departments app

from apps.departments.domain.entities.department import Department
from apps.departments.domain.services.department_service import DepartmentService
from apps.departments.domain.ports.department_port import DepartmentPort

__all__ = ['Department', 'DepartmentService', 'DepartmentPort']