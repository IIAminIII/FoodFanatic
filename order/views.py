from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from menu.models import CartItem

from .forms import OrderHistoryFilterForm
from .models import Order, OrderItem


@login_required(login_url="login")
@require_POST
@transaction.atomic
def place_order(request):
    cart_items = list(
        CartItem.objects.select_for_update()
        .filter(user=request.user)
        .select_related("product")
    )
    if not cart_items:
        messages.info(
            request,
            "Your cart is empty. Add an item before placing an order.",
        )
        return redirect("cart")

    unavailable = [item.product.title for item in cart_items if not item.product.is_available]
    if unavailable:
        messages.error(
            request,
            f"These items are no longer available: {', '.join(unavailable)}.",
        )
        return redirect("cart")

    # A cart price is only a quote. Charge the price that is live at checkout,
    # and let the customer re-confirm whenever that differs from what they saw.
    repriced = []
    for item in cart_items:
        current_price = item.product.current_price
        if current_price != item.unit_price:
            repriced.append((item.product.title, item.unit_price, current_price))
            item.unit_price = current_price
    if repriced:
        CartItem.objects.bulk_update(cart_items, ("unit_price",))
        changes = ", ".join(
            f"{title} is now {new_price} (was {old_price})"
            for title, old_price, new_price in repriced
        )
        messages.warning(
            request,
            f"Prices changed while the items were in your cart: {changes}. "
            "Review your cart and place the order again.",
        )
        return redirect("cart")

    total_amount = sum(
        (item.line_total for item in cart_items),
        start=Decimal("0.00"),
    )
    order = Order.objects.create(user=request.user, total_amount=total_amount)
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product=item.product,
                product_name=item.product.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in cart_items
        ]
    )
    CartItem.objects.filter(pk__in=[item.pk for item in cart_items]).delete()

    messages.success(request, "Your order has been placed successfully.")
    return redirect("order_details", order_id=order.id)


@login_required(login_url="login")
def order_details(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        pk=order_id,
        user=request.user,
    )
    return render(
        request,
        "order_details.html",
        {"order": order, "order_items": order.items.all()},
    )


@login_required(login_url="login")
@require_POST
@transaction.atomic
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order.objects.select_for_update(),
        pk=order_id,
        user=request.user,
    )
    if order.status != Order.Status.PENDING:
        messages.error(
            request,
            "This order is already being prepared and can no longer be "
            "cancelled. Please contact the restaurant.",
        )
    else:
        order.status = Order.Status.CANCELLED
        order.save(update_fields=("status",))
        messages.success(request, f"Order #{order.pk} has been cancelled.")
    return redirect("order_details", order_id=order.pk)


staff_required = user_passes_test(lambda user: user.is_staff, login_url="login")


@staff_required
def manage_orders(request):
    base = Order.objects.select_related("user").prefetch_related("items")
    active_orders = base.exclude(
        status__in=(Order.Status.COMPLETED, Order.Status.CANCELLED)
    ).order_by("placed_at")
    finished_today = base.filter(
        status__in=(Order.Status.COMPLETED, Order.Status.CANCELLED),
        placed_at__date=timezone.localdate(),
    )
    return render(
        request,
        "manage_orders.html",
        {"active_orders": active_orders, "finished_today": finished_today},
    )


@staff_required
@require_POST
@transaction.atomic
def update_order_status(request, order_id):
    order = get_object_or_404(Order.objects.select_for_update(), pk=order_id)
    action = request.POST.get("action")

    if action == "cancel" and order.is_open:
        order.status = Order.Status.CANCELLED
        order.save(update_fields=("status",))
        messages.success(request, f"Order #{order.pk} cancelled.")
    elif action == "advance" and order.next_status:
        order.status = order.next_status
        order.save(update_fields=("status",))
        messages.success(
            request,
            f"Order #{order.pk} moved to {order.get_status_display()}.",
        )
    else:
        messages.error(
            request, f"Order #{order.pk} cannot be updated from its current state."
        )
    return redirect("manage_orders")


class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = "orderhistory.html"
    model = Order
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .prefetch_related("items")
        )
        self.filter_form = OrderHistoryFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            start_date = self.filter_form.cleaned_data.get("start_date")
            end_date = self.filter_form.cleaned_data.get("end_date")
            if start_date:
                queryset = queryset.filter(placed_at__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(placed_at__date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context
