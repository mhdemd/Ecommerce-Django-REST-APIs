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

    @classmethod
    def remove_item(cls, user_id, product_id):
        key = cls.get_redis_cart_key(user_id)
        REDIS_CLIENT.hdel(key, product_id)

    @classmethod
    def set_item_quantity(cls, user_id, product_id, quantity):
        key = cls.get_redis_cart_key(user_id)
        if quantity <= 0:
            REDIS_CLIENT.hdel(key, product_id)
        else:
            REDIS_CLIENT.hset(key, product_id, quantity)

    @classmethod
    def get_all_items(cls, user_id):
        key = cls.get_redis_cart_key(user_id)
        return REDIS_CLIENT.hgetall(key)  # {product_id: quantity}

    @classmethod
    def clear_cart(cls, user_id):
        key = cls.get_redis_cart_key(user_id)
        REDIS_CLIENT.delete(key)