"""
URL configuration for HR & Employee Management Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets
from apps.employees.presentation.views import EmployeeViewSet
from apps.departments.presentation.views import DepartmentViewSet
from apps.leave.presentation.views import LeaveViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'leave', LeaveViewSet, basename='leave')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]