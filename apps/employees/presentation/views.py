"""
Employee Views

DRF ViewSet for Employee operations.
Thin HTTP layer - calls application commands and queries only.

Architecture Rule: Views MUST NOT import from infrastructure directly.
They go through application commands/queries.
"""

import logging
from uuid import UUID

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.common.exceptions import (
    DomainException,
    EmployeeNotFoundException,
    DuplicateEmailException,
    DuplicateEmployeeNumberException,
)
from apps.employees.presentation.serializers import (
    EmployeeSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    BulkDeleteSerializer,
)
from apps.employees.infrastructure.repository import EmployeeRepository
from apps.employees.application.commands.create_employee import CreateEmployeeCommand
from apps.employees.application.commands.update_employee import UpdateEmployeeCommand
from apps.employees.application.commands.delete_employee import DeleteEmployeeCommand
from apps.employees.application.queries.list_employees import ListEmployeesQuery
from apps.employees.application.queries.get_employee import GetEmployeeQuery
from apps.common.pagination import StandardPagination

logger = logging.getLogger(__name__)


class EmployeeViewSet(viewsets.ViewSet):
    """
    Employee ViewSet - handles all employee operations.
    
    Architecture Rule: Views only call application commands/queries.
    No ORM access directly. No infrastructure imports except repositories.
    """
    
    pagination_class = StandardPagination
    
    def list(self, request):
        """
        List all active employees with pagination and filters.
        
        GET /api/employees/
        GET /api/employees/?search=abebe
        GET /api/employees/?department=ENG
        GET /api/employees/?search=abebe&department=ENG&page=2
        """
        try:
            repository = EmployeeRepository()
            query = ListEmployeesQuery(repository)
            
            # Extract filters from query params
            filters = {
                'search': request.query_params.get('search'),
                'department': request.query_params.get('department'),
            }
            
            # Execute query
            employees = query.execute(filters)
            
            # Serialize
            serializer = EmployeeSerializer(employees, many=True)
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(serializer.data, request)
            
            return paginator.get_paginated_response(page)
            
        except Exception as e:
            logger.error(f"Error listing employees: {str(e)}")
            return Response(
                {'error': 'An error occurred while listing employees'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a single employee with nested department object.
        
        GET /api/employees/{id}/
        """
        try:
            repository = EmployeeRepository()
            query = GetEmployeeQuery(repository)
            employee = query.execute(UUID(pk))
            
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)
            
        except EmployeeNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(
                {'error': 'Invalid UUID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error retrieving employee: {str(e)}")
            return Response(
                {'error': 'An error occurred while retrieving the employee'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """
        Create a new employee.
        
        POST /api/employees/
        """
        try:
            serializer = EmployeeCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            repository = EmployeeRepository()
            command = CreateEmployeeCommand(repository)
            employee = command.execute(serializer.validated_data)
            
            response_serializer = EmployeeSerializer(employee)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except DuplicateEmailException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DuplicateEmployeeNumberException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating employee: {str(e)}")
            return Response(
                {'error': 'An error occurred while creating the employee'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """
        Full update of an employee.
        
        PUT /api/employees/{id}/
        """
        try:
            serializer = EmployeeUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            repository = EmployeeRepository()
            command = UpdateEmployeeCommand(repository)
            employee = command.execute(UUID(pk), serializer.validated_data)
            
            response_serializer = EmployeeSerializer(employee)
            return Response(response_serializer.data)
            
        except EmployeeNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DuplicateEmailException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating employee: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating the employee'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, pk=None):
        """
        Partial update of an employee.
        
        PATCH /api/employees/{id}/
        """
        # Same as update but with optional fields
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """
        Soft delete an employee (set is_active=False).
        
        DELETE /api/employees/{id}/
        
        Architecture Rule: Delete is always soft.
        Never hard delete employees.
        """
        try:
            repository = EmployeeRepository()
            command = DeleteEmployeeCommand(repository)
            command.execute(UUID(pk))
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except EmployeeNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting employee: {str(e)}")
            return Response(
                {'error': 'An error occurred while deleting the employee'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Deactivate multiple employees.
        
        POST /api/employees/bulk-delete/
        
        Request body:
        {
            "ids": ["uuid-1", "uuid-2", "uuid-3"]
        }
        
        Response:
        {
            "deactivated": 3,
            "already_inactive": 0,
            "not_found": 0
        }
        """
        try:
            serializer = BulkDeleteSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            repository = EmployeeRepository()
            result = repository.bulk_deactivate(serializer.validated_data['ids'])
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in bulk delete: {str(e)}")
            return Response(
                {'error': 'An error occurred during bulk delete'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )