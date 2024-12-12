import logging

from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta

from .utils_otp_and_tokens import store_verification_token

logger = logging.getLogger(__name__)
