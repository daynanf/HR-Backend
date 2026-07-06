"""
Fake Repository Implementations for Unit Testing

These are in-memory implementations of the port interfaces.
They allow testing domain logic without a database.

Architecture Rule: Unit tests use fake repositories, not the real ones.
"""

from typing import Optional, List, Dict
from uuid import UUID
from datetime import date, datetime
from copy import deepcopy

from apps.employees.domain.entities.employee import Employee
from apps.employees.domain.ports.employee_port import EmployeePort

from apps.departments.domain.entities.department import Department
from apps.departments.domain.ports.department_port import DepartmentPort

from apps.leave.domain.entities.leave_request import LeaveRequest
from apps.leave.domain.ports.leave_port import LeavePort

from apps.common.exceptions import (
    EmployeeNotFoundException,
    DuplicateEmailException,
    DuplicateEmployeeNumberException,
)


class FakeEmployeeRepository(EmployeePort):
    """
    In-memory fake repository for Employee unit testing.
    
    Uses a dictionary as the storage backend.
    No database, no Django - pure Python.
    """
    
    def __init__(self):
        self._store: Dict[UUID, Employee] = {}
        self._email_index: Dict[str, UUID] = {}
        self._number_index: Dict[str, UUID] = {}
    
    def create(self, employee: Employee) -> Employee:
        """Persist a new employee in memory."""
        if employee.email in self._email_index:
            raise DuplicateEmailException(f"Email '{employee.email}' already exists")
        if employee.employee_number in self._number_index:
            raise DuplicateEmployeeNumberException(
                f"Employee number '{employee.employee_number}' already exists"
            )
        
        self._store[employee.id] = employee
        self._email_index[employee.email] = employee.id
        self._number_index[employee.employee_number] = employee.id
        return employee
    
    def get_by_id(self, id: UUID) -> Optional[Employee]:
        """Retrieve an employee by UUID from memory."""
        return self._store.get(id)
    
    def get_by_email(self, email: str) -> Optional[Employee]:
        """Retrieve an employee by email from memory."""
        employee_id = self._email_index.get(email)
        if employee_id:
            return self._store.get(employee_id)
        return None
    
    def get_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        """Retrieve an employee by employee number from memory."""
        employee_id = self._number_index.get(employee_number)
        if employee_id:
            return self._store.get(employee_id)
        return None
    
    def list_active(self, filters: Dict[str, str]) -> List[Employee]:
        """List active employees with optional filters."""
        employees = [e for e in self._store.values() if e.is_active]
        
        search = filters.get('search')
        if search:
            search_lower = search.lower()
            employees = [
                e for e in employees
                if search_lower in e.first_name.lower() or
                search_lower in e.last_name.lower()
            ]
        
        department = filters.get('department')
        if department:
            # In a real repo, this would join with department table
            # For fake, we just check if department code matches
            # We'll assume department_id contains the code for simplicity
            employees = [
                e for e in employees
                if str(e.department_id).startswith(department.lower())
            ]
        
        return employees
    
    def update(self, employee: Employee) -> Employee:
        """Update an existing employee in memory."""
        if employee.id not in self._store:
            raise EmployeeNotFoundException(f"Employee {employee.id} not found")
        
        # Check email conflict
        existing_email_employee_id = self._email_index.get(employee.email)
        if existing_email_employee_id and existing_email_employee_id != employee.id:
            raise DuplicateEmailException(f"Email '{employee.email}' already exists")
        
        self._store[employee.id] = employee
        self._email_index[employee.email] = employee.id
        self._number_index[employee.employee_number] = employee.id
        return employee
    
    def soft_delete(self, id: UUID) -> bool:
        """Soft delete an employee in memory."""
        if id not in self._store:
            raise EmployeeNotFoundException(f"Employee {id} not found")
        
        employee = self._store[id]
        employee.is_active = False
        return True
    
    def bulk_deactivate(self, ids: List[UUID]) -> Dict[str, int]:
        """Deactivate multiple employees in memory."""
        result = {
            'deactivated': 0,
            'already_inactive': 0,
            'not_found': 0,
        }
        
        for id in ids:
            if id not in self._store:
                result['not_found'] += 1
            elif not self._store[id].is_active:
                result['already_inactive'] += 1
            else:
                self._store[id].is_active = False
                result['deactivated'] += 1
        
        return result
    
    def get_next_employee_number(self) -> str:
        """Generate the next employee number."""
        if not self._store:
            return 'EMP-001'
        
        numbers = [e.employee_number for e in self._store.values()]
        last_number = max([int(n.split('-')[1]) for n in numbers if n.startswith('EMP-')])
        return f"EMP-{last_number + 1:03d}"
    
    def clear(self):
        """Clear all data (useful for test cleanup)."""
        self._store.clear()
        self._email_index.clear()
        self._number_index.clear()


class FakeDepartmentRepository(DepartmentPort):
    """
    In-memory fake repository for Department unit testing.
    """
    
    def __init__(self):
        self._store: Dict[UUID, Department] = {}
        self._code_index: Dict[str, UUID] = {}
        self._employee_counts: Dict[UUID, int] = {}
    
    def create(self, department: Department) -> Department:
        """Persist a new department in memory."""
        if department.code in self._code_index:
            raise ValueError(f"Department code '{department.code}' already exists")
        
        self._store[department.id] = department
        self._code_index[department.code] = department.id
        self._employee_counts[department.id] = 0
        return department
    
    def get_by_id(self, id: UUID) -> Optional[Department]:
        """Retrieve a department by UUID from memory."""
        return self._store.get(id)
    
    def get_by_code(self, code: str) -> Optional[Department]:
        """Retrieve a department by code from memory."""
        department_id = self._code_index.get(code.upper())
        if department_id:
            return self._store.get(department_id)
        return None
    
    def list_all(self) -> List[Department]:
        """List all departments from memory."""
        return list(self._store.values())
    
    def update(self, department: Department) -> Department:
        """Update an existing department in memory."""
        if department.id not in self._store:
            raise ValueError(f"Department {department.id} not found")
        
        # Check code conflict
        existing_id = self._code_index.get(department.code)
        if existing_id and existing_id != department.id:
            raise ValueError(f"Department code '{department.code}' already exists")
        
        self._store[department.id] = department
        self._code_index[department.code] = department.id
        return department
    
    def deactivate(self, id: UUID) -> bool:
        """Deactivate a department in memory."""
        if id not in self._store:
            raise ValueError(f"Department {id} not found")
        
        # Check for active employees
        if self._employee_counts.get(id, 0) > 0:
            raise ValueError(f"Cannot deactivate department with active employees")
        
        self._store[id].is_active = False
        return True
    
    def get_active_employee_count(self, department_id: UUID) -> int:
        """Get the number of active employees in a department."""
        return self._employee_counts.get(department_id, 0)
    
    def set_employee_count(self, department_id: UUID, count: int):
        """Set the employee count (for testing purposes)."""
        self._employee_counts[department_id] = count
    
    def clear(self):
        """Clear all data."""
        self._store.clear()
        self._code_index.clear()
        self._employee_counts.clear()


class FakeLeaveRepository(LeavePort):
    """
    In-memory fake repository for LeaveRequest unit testing.
    """
    
    def __init__(self):
        self._store: Dict[UUID, LeaveRequest] = {}
        self._employee_leaves: Dict[UUID, List[UUID]] = {}
    
    def submit(self, leave: LeaveRequest) -> LeaveRequest:
        """Submit a new leave request in memory."""
        self._store[leave.id] = leave
        if leave.employee_id not in self._employee_leaves:
            self._employee_leaves[leave.employee_id] = []
        self._employee_leaves[leave.employee_id].append(leave.id)
        return leave
    
    def get_by_id(self, id: UUID) -> Optional[LeaveRequest]:
        """Retrieve a leave request by UUID from memory."""
        return self._store.get(id)
    
    def list_for_employee(self, employee_id: UUID) -> List[LeaveRequest]:
        """List all leave requests for an employee from memory."""
        leave_ids = self._employee_leaves.get(employee_id, [])
        return [self._store[id] for id in leave_ids if id in self._store]
    
    def approve(self, id: UUID, reviewed_by: UUID) -> LeaveRequest:
        """Approve a leave request in memory."""
        if id not in self._store:
            raise ValueError(f"Leave request {id} not found")
        
        leave = self._store[id]
        if leave.status != 'PENDING':
            raise ValueError(f"Cannot approve a leave request with status '{leave.status}'")
        
        leave.status = 'APPROVED'
        leave.reviewed_by = reviewed_by
        leave.reviewed_at = datetime.now()
        return leave
    
    def reject(self, id: UUID, reviewed_by: UUID) -> LeaveRequest:
        """Reject a leave request in memory."""
        if id not in self._store:
            raise ValueError(f"Leave request {id} not found")
        
        leave = self._store[id]
        if leave.status != 'PENDING':
            raise ValueError(f"Cannot reject a leave request with status '{leave.status}'")
        
        leave.status = 'REJECTED'
        leave.reviewed_by = reviewed_by
        leave.reviewed_at = datetime.now()
        return leave
    
    def get_on_leave_count(self, as_of_date: date) -> int:
        """Count employees on approved leave on a specific date."""
        employees_on_leave = set()
        
        for leave in self._store.values():
            if leave.status == 'APPROVED':
                if leave.start_date <= as_of_date <= leave.end_date:
                    employees_on_leave.add(leave.employee_id)
        
        return len(employees_on_leave)
    
    def list_all(self, filters: Dict[str, str]) -> List[LeaveRequest]:
        """List all leave requests with filters."""
        leaves = list(self._store.values())
        
        status = filters.get('status')
        if status:
            leaves = [l for l in leaves if l.status == status.upper()]
        
        department = filters.get('department')
        if department:
            # In a real repo, this would join with employee -> department
            # For testing, we'll just filter by a mock department_id
            leaves = [l for l in leaves if str(l.employee_id).startswith(department.lower())]
        
        return leaves
    
    def clear(self):
        """Clear all data."""
        self._store.clear()
        self._employee_leaves.clear()