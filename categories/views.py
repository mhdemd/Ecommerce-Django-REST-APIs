from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .models import Category
from .permissions import IsAdminUserOrReadOnly
from .serializers import CategorySerializer
