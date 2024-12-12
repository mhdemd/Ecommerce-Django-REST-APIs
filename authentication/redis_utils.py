from django.conf import settings


def save_to_redis(key, value, ttl=None):
    # Save a value under a given key with an optional time-to-live (ttl) in seconds.
    # This function relies on settings.redis_instance which should be a redis.StrictRedis instance.
    if ttl:
        settings.redis_instance.setex(key, ttl, value)
    else:
        settings.redis_instance.set(key, value)
