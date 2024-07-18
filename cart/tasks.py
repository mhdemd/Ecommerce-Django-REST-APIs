from datetime import datetime

from celery import shared_task
from dateutil import parser

from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.utils import timezone
from shop.models import ProductInventory


@shared_task
def update_session_data(session_key, new_data):
    try:
        session = Session.objects.get(session_key=session_key)
        # session_data = session.get_decoded()

        # Create new session_store
        session_store = SessionStore(session_key=session.session_key)

        # Add changes to session_store
        session_store["cart"] = new_data.get("cart", {})

        # store session_store
        session_store.save()
    except Session.DoesNotExist:
        pass


@shared_task
def display_sessions():
    # Session.objects.all().delete()

    # Here we extract the active sessions from the database
    sessions = Session.objects.filter(expire_date__gt=timezone.now())
    current_datetime = datetime.now()

    for session in sessions:
        session_data = session.get_decoded()
        print(session_data)

        my_dict = session_data["cart"]
        if my_dict:
            all_expired = True

            for key, item in my_dict.items():
                expiry_date_str = item.get("expiry_date", "")  # If there is no date
                expiry_datetime = parser.parse(expiry_date_str)

                if current_datetime <= expiry_datetime:
                    # We change the flag to False if none have expired
                    all_expired = False
                    break

            # If all have expired, clear all keys and then update session data
            if all_expired:
                for key, item in my_dict.items():
                    product_inventry_id = key
                    quantity = item.get("quantity", "")
                    productinventory = ProductInventory.objects.get(
                        id=product_inventry_id
                    )
                    productinventory.stock += quantity
                    productinventory.save()  # به‌روزرسانی موجودی کالا
                my_dict.clear()
                update_session_data(session.session_key, {"cart": my_dict})
