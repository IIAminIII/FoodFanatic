from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from menu.models import CartItem, FoodItem

from .models import Order, OrderItem


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("customer", password="test-password")
        self.other_user = User.objects.create_user("other", password="test-password")
        self.item = FoodItem.objects.create(
            title="Burger",
            description="Fresh burger",
            price=Decimal("10.00"),
        )
        self.client.force_login(self.user)

    def test_checkout_is_post_only_and_preserves_order_item_snapshot(self):
        CartItem.objects.create(
            user=self.user,
            product=self.item,
            quantity=2,
            unit_price=Decimal("8.50"),
        )
        url = reverse("placeorder")

        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url)

        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse("order_details", args=(order.pk,)))
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        order_item = OrderItem.objects.get(order=order)
        self.assertEqual(order_item.product, self.item)
        self.assertEqual(order_item.product_name, "Burger")
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.unit_price, Decimal("8.50"))
        self.assertEqual(order.total_amount, Decimal("17.00"))

    def test_empty_cart_does_not_create_order(self):
        response = self.client.post(reverse("placeorder"))

        self.assertRedirects(response, reverse("cart"))
        self.assertFalse(Order.objects.exists())

    def test_unavailable_item_blocks_checkout_without_clearing_cart(self):
        self.item.is_available = False
        self.item.save(update_fields=("is_available",))
        CartItem.objects.create(
            user=self.user,
            product=self.item,
            unit_price=Decimal("10.00"),
        )

        response = self.client.post(reverse("placeorder"))

        self.assertRedirects(response, reverse("cart"))
        self.assertFalse(Order.objects.exists())
        self.assertTrue(CartItem.objects.filter(user=self.user).exists())

    def test_user_cannot_view_another_users_order(self):
        order = Order.objects.create(
            user=self.other_user,
            total_amount=Decimal("10.00"),
        )

        response = self.client.get(reverse("order_details", args=(order.pk,)))

        self.assertEqual(response.status_code, 404)

    def test_invalid_history_date_range_is_handled(self):
        response = self.client.get(
            reverse("orderhistory"),
            {"start_date": "2026-02-02", "end_date": "2026-01-01"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "start date must be before")
