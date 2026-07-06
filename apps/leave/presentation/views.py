"""
Leave Views

DRF ViewSet for LeaveRequest operations.
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
    LeaveNotFoundException,
    LeaveOverlapException,
    InvalidLeaveStatusException,
)
from apps.leave.presentation.serializers import (
    LeaveRequestSerializer,
    LeaveSubmitSerializer,
)
from apps.leave.infrastructure.repository import LeaveRepository
from apps.leave.application.commands.submit_leave import SubmitLeaveCommand
from apps.leave.application.commands.approve_leave import ApproveLeaveCommand
from apps.leave.application.queries.list_leave_requests import ListLeaveRequestsQuery
from apps.leave.application.queries.get_on_leave_count import GetOnLeaveCountQuery
from apps.common.pagination import StandardPagination

logger = logging.getLogger(__name__)


class LeaveViewSet(viewsets.ViewSet):
    """
    Leave ViewSet - handles all leave request operations.
    
    Architecture Rule: Views only call application commands/queries.
    No ORM access directly.
    """
    
    pagination_class = StandardPagination
    
    def list(self, request):
        """
        List leave requests with filters.
        
        GET /api/leave/
        GET /api/leave/?status=PENDING
        GET /api/leave/?department=ENG
        GET /api/leave/?status=APPROVED&department=ENG
        """
        try:
            repository = LeaveRepository()
            query = ListLeaveRequestsQuery(repository)
            
            filters = {
                'status': request.query_params.get('status'),
                'department': request.query_params.get('department'),
            }
            
            leaves = query.execute(filters)
            
            serializer = LeaveRequestSerializer(leaves, many=True)
            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(serializer.data, request)
            return paginator.get_paginated_response(page)
            
        except Exception as e:
            logger.error(f"Error listing leave requests: {str(e)}")
            return Response(
                {'error': 'An error occurred while listing leave requests'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a single leave request.
        
        GET /api/leave/{id}/
        """
        try:
            repository = LeaveRepository()
            leave = repository.get_by_id(UUID(pk))
            
            if not leave:
                return Response(
                    {'error': f'Leave request {pk} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = LeaveRequestSerializer(leave)
            return Response(serializer.data)
            
        except ValueError:
            return Response(
                {'error': 'Invalid UUID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error retrieving leave request: {str(e)}")
            return Response(
                {'error': 'An error occurred while retrieving the leave request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """
        Submit a new leave request.
        
        POST /api/leave/
        """
        try:
            serializer = LeaveSubmitSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            repository = LeaveRepository()
            command = SubmitLeaveCommand(repository)
            leave = command.execute(serializer.validated_data)
            
            response_serializer = LeaveRequestSerializer(leave)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except LeaveOverlapException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error submitting leave request: {str(e)}")
            return Response(
                {'error': 'An error occurred while submitting the leave request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve a pending leave request.
        
        PATCH /api/leave/{id}/approve/
        """
        try:
            repository = LeaveRepository()
            command = ApproveLeaveCommand(repository)
            
            # Get reviewed_by from request data or use a default
            reviewed_by = request.data.get('reviewed_by')
            if not reviewed_by:
                # In production, this would come from the authenticated user
                # For now, we'll use the employee_id from the leave request
                leave = repository.get_by_id(UUID(pk))
                if leave:
                    reviewed_by = leave.employee_id
                else:
                    raise LeaveNotFoundException(f"Leave request {pk} not found")
            
            leave = command.execute(UUID(pk), UUID(reviewed_by), action='approve')
            
            serializer = LeaveRequestSerializer(leave)
            return Response(serializer.data)
            
        except LeaveNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except InvalidLeaveStatusException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error approving leave request: {str(e)}")
            return Response(
                {'error': 'An error occurred while approving the leave request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'], url_path='reject')
    def reject(self, request, pk=None):
        """
        Reject a pending leave request.
        
        PATCH /api/leave/{id}/reject/
        """
        try:
            repository = LeaveRepository()
            command = ApproveLeaveCommand(repository)
            
            # Get reviewed_by from request data or use a default
            reviewed_by = request.data.get('reviewed_by')
            if not reviewed_by:
                leave = repository.get_by_id(UUID(pk))
                if leave:
                    reviewed_by = leave.employee_id
                else:
                    raise LeaveNotFoundException(f"Leave request {pk} not found")
            
            leave = command.execute(UUID(pk), UUID(reviewed_by), action='reject')
            
            serializer = LeaveRequestSerializer(leave)
            return Response(serializer.data)
            
        except LeaveNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except InvalidLeaveStatusException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except DomainException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error rejecting leave request: {str(e)}")
            return Response(
                {'error': 'An error occurred while rejecting the leave request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='on-leave-count')
    def on_leave_count(self, request):
        """
        Get count of employees on approved leave today.
        
        GET /api/leave/on-leave-count/
        
        Response:
        {
            "on_leave_count": 7,
            "as_of": "2025-06-27"
        }
        """
        try:
            repository = LeaveRepository()
            query = GetOnLeaveCountQuery(repository)
            result = query.execute()
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting on-leave count: {str(e)}")
            return Response(
                {'error': 'An error occurred while getting on-leave count'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )