"""
Custom DRF exception handler for consistent error responses.

Architecture Rule: All DomainException violations return HTTP 400 with a clear message.
"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

from apps.common.exceptions import DomainException


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts DomainExceptions to 400 responses.
    
    This ensures:
    1. All business rule violations return HTTP 400 (not 500)
    2. Error messages are clear and actionable
    3. Consistent error response format
    
    Args:
        exc: The exception instance
        context: DRF exception context
    
    Returns:
        Response: DRF response with appropriate status code
    """
    # Let DRF handle standard HTTP exceptions
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        return response
    
    # Handle domain exceptions - all business rule violations
    if isinstance(exc, DomainException):
        return Response(
            {
                'error': str(exc),
                'type': exc.__class__.__name__,
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle ValueError (domain layer raises ValueError for basic validation)
    if isinstance(exc, ValueError):
        return Response(
            {
                'error': str(exc),
                'type': 'ValueError',
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle any other exceptions as 500
    return Response(
        {
            'error': 'An internal server error occurred.',
            'type': 'InternalServerError',
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )