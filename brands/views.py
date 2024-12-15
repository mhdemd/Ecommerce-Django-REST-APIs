from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Brand
from .serializers import BrandSerializer


class BrandPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = BrandPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name", "created_at"]
    search_fields = ["name", "description", "slug"]
