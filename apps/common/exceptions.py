"""
Domain Exceptions - All business rule violations are raised as DomainException subclasses.

These exceptions are raised in the Domain layer and caught in the Presentation layer.
The Presentation layer converts them to HTTP 400 responses.

Architecture Rule: Domain layer NEVER raises HTTP exceptions.
"""


class DomainException(Exception):
    """
    Base exception for all domain-level business rule violations.
    
    All domain business rules should raise this or a subclass of this.
    This ensures the Presentation layer can catch all domain errors uniformly.
    """
    pass


class EmployeeNotFoundException(DomainException):
    """Raised when an employee cannot be found by ID or email."""
    pass


class DuplicateEmailException(DomainException):
    """Raised when an attempt is made to create/update an employee with a duplicate email."""
    pass


class DuplicateEmployeeNumberException(DomainException):
    """Raised when an attempt is made to create an employee with a duplicate employee number."""
    pass


class LeaveOverlapException(DomainException):
    """Raised when a leave request overlaps with an existing approved leave request."""
    pass


class InvalidLeaveStatusException(DomainException):
    """Raised when an invalid status transition is attempted on a leave request."""
    pass


class LeaveNotFoundException(DomainException):
    """Raised when a leave request cannot be found by ID."""
    pass


class DepartmentHasActiveEmployeesException(DomainException):
    """Raised when an attempt is made to deactivate a department that has active employees."""
    pass


class DepartmentNotFoundException(DomainException):
    """Raised when a department cannot be found by ID or code."""
    pass


class DuplicateDepartmentCodeException(DomainException):
    """Raised when an attempt is made to create a department with a duplicate code."""
    pass


class InvalidEmploymentTypeException(DomainException):
    """Raised when an invalid employment type is provided."""
    pass