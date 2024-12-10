from django.contrib.sessions.models import Session
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import SessionInfo


@receiver(post_save, sender=Session)
def create_or_update_session_info(sender, instance, created, **kwargs):
    if created:
        SessionInfo.objects.create(session=instance)
    else:
        SessionInfo.objects.update_or_create(session=instance)


@receiver(post_delete, sender=Session)
def delete_session_info(sender, instance, **kwargs):
    SessionInfo.objects.filter(session=instance).delete()
