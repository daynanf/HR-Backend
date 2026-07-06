"""
Custom pagination for consistent API responses.

All list endpoints use StandardPagination to ensure consistent
page structure across the API.
"""

from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Standard pagination class for all API endpoints.
    
    Features:
    - Default page size: 20
    - Clients can override with ?page_size=50
    - Maximum page size: 100
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Override to ensure consistent response structure.
        
        Response format:
        {
            "count": 42,
            "next": "http://localhost:8000/api/employees/?page=2",
            "previous": null,
            "results": [...]
        }
        """
        return super().get_paginated_response(data)