from django.urls import path

from .views import (  # User Endpoints; Admin Endpoints
    AdminCategoryDetailView,
    AdminCategoryListCreateView,
    CategoryDetailView,
    CategoryListView,
)
