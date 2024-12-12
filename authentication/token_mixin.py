import logging

from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta

from .utils_otp_and_tokens import store_verification_token

logger = logging.getLogger(__name__)


class TokenMixin:
    def generate_token(self, user, expiry_hours=1):
        # Generate a secure token and store it in Redis with an expiration time
        token = get_random_string(32)
        token_expiration = now() + timedelta(hours=expiry_hours)

        # Convert expiration to seconds
        ttl = int((token_expiration - now()).total_seconds())

        # Store the token with the user_id in Redis
        # Redis will handle expiration automatically
        store_verification_token(token, user.id, ttl=ttl)

        logger.info(
            f"Token for user {user.id} generated and stored in Redis with TTL {ttl} seconds."
        )

        return token
