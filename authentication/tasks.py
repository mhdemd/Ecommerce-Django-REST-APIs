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


# ---------------------------------------------------------
# GenerateOTPView with Email
# ---------------------------------------------------------
@shared_task
def send_otp_via_email(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)


# ---------------------------------------------------------
# GenerateOTPView with SMS
# ---------------------------------------------------------
@shared_task
def send_otp_via_sms(phone_number, otp):
    # This section is for integration with the SMS service.
    print(f"Send SMS to {phone_number} with OTP: {otp}")
