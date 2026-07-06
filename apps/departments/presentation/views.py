"""
Department Views

DRF ViewSet for Department operations.
Thin HTTP layer - calls application commands and queries only.
"""

import logging
from uuid import UUID

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.common.exceptions import (
    DomainException,
    DepartmentNotFoundException,
    DuplicateDepartmentCodeException,
    DepartmentHasActiveEmployeesException,
)
from apps.departments.presentation.serializers import DepartmentSerializer
from apps.departments.infrastructure.repository import DepartmentRepository
from apps.departments.application.queries.list_departments import ListDepartmentsQuery
from apps.departments.application.commands.create_department import CreateDepartmentCommand
from apps.departments.application.commands.update_department import UpdateDepartmentCommand

logger = logging.getLogger(__name__)


class DepartmentViewSet(viewsets.ViewSet):
    """
    Department ViewSet - handles all department operations.
    
    Architecture Rule: Views only call application commands/queries.
    No ORM access directly. No infrastructure imports except repositories.
    """
    
    def list(self, request):
        """
        List all departments.
        
        GET /api/departments/
        """
        try:
            repository = DepartmentRepository()
            query = ListDepartmentsQuery(repository)
            departments = query.execute()
            
            serializer = DepartmentSerializer(departments, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error listing departments: {str(e)}")
            return Response(
                {'error': 'An error occurred while listing departments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a single department.
        
        GET /api/departments/{id}/
        """
        try:
            repository = DepartmentRepository()
            department = repository.get_by_id(UUID(pk))
            
            if not department:
                return Response(
                    {'error': f'Department {pk} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = DepartmentSerializer(department)
            return Response(serializer.data)
            
        except ValueError:
            return Response(
                {'error': 'Invalid UUID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error retrieving department: {str(e)}")
            return Response(
                {'error': 'An error occurred while retrieving the department'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """
        Create a new department.
        
        POST /api/departments/
        """
        try:
            serializer = DepartmentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            repository = DepartmentRepository()
            command = CreateDepartmentCommand(repository)
            department = command.execute(serializer.validated_data)
            
            response_serializer = DepartmentSerializer(department)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except DuplicateDepartmentCodeException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating department: {str(e)}")
            return Response(
                {'error': 'An error occurred while creating the department'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """
        Full update of a department.
        
        PUT /api/departments/{id}/
        """
        try:
            serializer = DepartmentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            repository = DepartmentRepository()
            command = UpdateDepartmentCommand(repository)
            department = command.execute(UUID(pk), serializer.validated_data)
            
            response_serializer = DepartmentSerializer(department)
            return Response(response_serializer.data)
            
        except DepartmentNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DuplicateDepartmentCodeException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating department: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating the department'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        """
        Deactivate a department.
        
        POST /api/departments/{id}/deactivate/
        """
        try:
            repository = DepartmentRepository()
            result = repository.deactivate(UUID(pk))
            
            return Response(
                {'message': f'Department {pk} deactivated successfully'},
                status=status.HTTP_200_OK
            )
            
        except DepartmentNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except DepartmentHasActiveEmployeesException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deactivating department: {str(e)}")
            return Response(
                {'error': 'An error occurred while deactivating the department'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )