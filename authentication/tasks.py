from celery import shared_task
from django.core.mail import send_mail


# ---------------------------------------------------------
# RegisterView
# ---------------------------------------------------------
@shared_task
def send_verification_email(subject, message, from_email, recipient_list):
    try:
        send_mail(subject, message, from_email, recipient_list)
        return f"Email sent to {recipient_list}"
    except Exception as e:
        return f"Failed to send email: {e}"


# ---------------------------------------------------------
# ForgotPasswordView
# ---------------------------------------------------------
@shared_task
def send_reset_password_email(subject, message, from_email, recipient_list):
    try:
        send_mail(subject, message, from_email, recipient_list)
        return f"Password reset email sent to {recipient_list}"
    except Exception as e:
        return f"Failed to send email: {e}"
