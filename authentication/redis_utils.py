from django.conf import settings


def save_to_redis(key, value, ttl=None):
    if ttl:
        settings.REDIS_INSTANCE.setex(key, ttl, value)
    else:
        settings.REDIS_INSTANCE.set(key, value)


def get_from_redis(key):
    return settings.REDIS_INSTANCE.get(key)


def delete_from_redis(key):
    return settings.REDIS_INSTANCE.delete(key)
