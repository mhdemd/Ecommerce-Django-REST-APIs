# This file contains the synchronization logic with Redis.
import json

from django.conf import settings

REDIS_CLIENT = settings.REDIS_INSTANCE


class CartService:
    @staticmethod
    def get_redis_cart_key(user_id):
        return f"cart:{user_id}"

    @classmethod
    def add_item(cls, user_id, product_id, quantity=1):
        key = cls.get_redis_cart_key(user_id)
        current_qty = REDIS_CLIENT.hget(key, product_id)
        if current_qty:
            quantity += int(current_qty)
        REDIS_CLIENT.hset(key, product_id, quantity)
        return quantity
