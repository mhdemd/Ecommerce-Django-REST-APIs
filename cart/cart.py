from datetime import datetime
from decimal import ROUND_DOWN, Decimal

from checkout.models import DeliveryOptions
from django.conf import settings
from django.utils import timezone
from shop.models import Product, ProductInventory

# from celery import shared_task


class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(
        self,
        product_id,
        product_inventory_id,
        variety,
        sale_price,
        quantity=1,
        override_quantity=False,
    ):
        """
        Add the product to the cart.
        """
        product_inventory_id = str(product_inventory_id)

        if product_inventory_id not in self.cart:
            self.cart[product_inventory_id] = {
                "product_id": product_id,
                "quantity": 0,
                "variety": variety,
                "sale_price": sale_price,
            }

        product_inventory = ProductInventory.objects.get(id=product_inventory_id)

        if override_quantity:
            # Increase or decrease the stock according to the quantity update of the cart details
            initial_quantity = self.cart[product_inventory_id]["quantity"]
            if quantity >= initial_quantity:
                product_inventory.stock -= quantity - initial_quantity
            else:
                product_inventory.stock += initial_quantity - quantity
            # Add new quantity to cart's dict
            self.cart[product_inventory_id]["quantity"] = quantity
        else:
            # Decrease the stock
            product_inventory.stock -= quantity
            # Add new quantity to cart's dict
            self.cart[product_inventory_id]["quantity"] += quantity

        product_inventory.save()

        expiry_time = (timezone.now() + timezone.timedelta(minutes=2)).isoformat()
        self.cart[product_inventory_id]["expiry_date"] = expiry_time

        self.save()

    def save(self):
        """
        Save the cart.
        """
        self.session.modified = True

    def remove(self, product_inventory):
        """
        Remove a product from the cart.
        """
        product_inventory_id = str(product_inventory.id)

        # Check if the product_inventory_id is in the cart
        if product_inventory_id in self.cart:
            quantity = self.cart[product_inventory_id]["quantity"]
            product_inventory = ProductInventory.objects.get(id=product_inventory_id)
            product_inventory.stock += quantity
            product_inventory.save()
            del self.cart[product_inventory_id]
            self.save()
        else:
            pass

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = [item["product_id"] for item in self.cart.values()]
        unique_product_ids = list(set(product_ids))
        cart = self.cart.copy()

        for i in range(len(unique_product_ids)):
            product_inventory_ids = [
                key
                for key, value in self.cart.items()
                if value["product_id"] == unique_product_ids[i]
            ]
            for j in range(len(product_inventory_ids)):
                product = Product.objects.get(id=unique_product_ids[i])
                cart[str(product_inventory_ids[j])]["product"] = product

        for item in cart.values():
            sale_price = float(item["sale_price"])
            item["sale_price"] = sale_price
            item["total_price"] = item["sale_price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        del self.session["address"]
        del self.session["purchase"]
        self.save()

    def get_quantity_for_product(self):
        """
        Get quantities and product inventory IDs for all products in the cart.
        """
        quantities = {}
        for product_inventory_id, item_data in self.cart.items():
            quantities[product_inventory_id] = item_data["quantity"]
        return quantities

    def cart_update_delivery(self, deliveryprice=0):
        subtotal = sum(
            Decimal(item["sale_price"]) * item["quantity"]
            for item in self.cart.values()
        )
        total = subtotal + Decimal(deliveryprice)
        return total.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    def get_delivery_price(self):
        newprice = Decimal("0.00")  # Initialize newprice as Decimal

        if "purchase" in self.session:
            newprice = DeliveryOptions.objects.get(
                id=self.session["purchase"]["delivery_id"]
            ).delivery_price

        return newprice.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    def get_subtotal_price(self):
        subtotal = Decimal(0)  # Initialize subtotal as a Decimal
        for item in self.cart.values():
            subtotal += Decimal(item["sale_price"]) * item["quantity"]
        return subtotal.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    def get_total_price(self):
        """
        Get the total price of all items in the cart.
        """

        newprice = Decimal("0.00")
        subtotal = sum(
            Decimal(item["sale_price"]) * item["quantity"]
            for item in self.cart.values()
        )

        if "purchase" in self.session:
            newprice = DeliveryOptions.objects.get(
                id=self.session["purchase"]["delivery_id"]
            ).delivery_price

        total = subtotal + Decimal(newprice)
        # قسمت کلیدی: تبدیل عدد نهایی به دو رقم اعشار
        total = total.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        return total

    def get_latest_expiry_time(self):
        """
        Find the latest expiry time among all product inventories in the cart.
        """
        latest_expiry = None

        for item in self.cart.values():
            expiry_time_str = item.get("expiry_date")

            if expiry_time_str:
                expiry_time = timezone.make_aware(
                    datetime.fromisoformat(expiry_time_str)
                )

                if latest_expiry is None or expiry_time > latest_expiry:
                    latest_expiry = expiry_time

        return latest_expiry

    def get_expiry_time_remaining(self):
        """
        Calculate the remaining time until the latest expiry time in the cart.
        """
        latest_expiry = self.get_latest_expiry_time()

        if latest_expiry:
            latest_expiry = latest_expiry.replace(tzinfo=None)  # تبدیل به offset-naive
            current_time = datetime.utcnow().replace(
                tzinfo=None
            )  # تبدیل به offset-naive
            remaining_time = latest_expiry - current_time
            remaining_minutes = remaining_time.total_seconds() // 60
            remaining_seconds = remaining_time.total_seconds() % 60
            return int(remaining_minutes), int(remaining_seconds)
        else:
            return None
