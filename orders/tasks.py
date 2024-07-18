from celery import shared_task

from django.core.mail import send_mail

from .models import Order


@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f"Order nr. {order.id}"
    message = (
        f"Dear {order.user.first_name},\n\n"
        f"You have successfully placed an order."
        f"Your order ID is {order.id}."
    )
    mail_sent = send_mail(
        subject, message, "mahdi.emadi90@gmail.com", [order.user.email]
    )
    return mail_sent
