# tasks.py (assuming already defined tasks for sending emails and SMS)
from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_otp_via_email(subject, message, from_email, recipient_list):
    # Sends the OTP via email asynchronously
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_otp_via_sms(phone_number, otp):
    # Placeholder for sending OTP via SMS
    # Integration with an SMS service should be done here.
    # Do not print sensitive info in production logs.
    pass
