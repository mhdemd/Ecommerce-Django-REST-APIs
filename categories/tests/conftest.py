import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from categories.models import Category

User = get_user_model()
