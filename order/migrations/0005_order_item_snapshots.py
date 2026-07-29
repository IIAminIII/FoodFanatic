from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def snapshot_order_items(apps, schema_editor):
    Order = apps.get_model("order", "Order")
    OrderItem = apps.get_model("order", "OrderItem")

    for order_item in OrderItem.objects.select_related("cartitem__product"):
        order_item.product_id = order_item.cartitem.product_id
        order_item.product_name = order_item.cartitem.product.title
        order_item.save(update_fields=("product", "product_name"))

    for order in Order.objects.all():
        total = sum(
            (
                item.unit_price * item.quantity
                for item in OrderItem.objects.filter(order=order)
            ),
            start=Decimal("0.00"),
        )
        order.total_amount = total
        order.save(update_fields=("total_amount",))


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0005_phase1_integrity"),
        ("order", "0004_delete_specialoffer"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ("-placed_at",)},
        ),
        migrations.AlterModelOptions(
            name="orderitem",
            options={"ordering": ("id",)},
        ),
        migrations.AlterField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PREPARING", "Preparing"),
                    ("READY", "Ready"),
                    ("COMPLETED", "Completed"),
                    ("CANCELLED", "Cancelled"),
                ],
                db_index=True,
                default="PENDING",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="total_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=12,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0.00"))
                ],
            ),
        ),
        migrations.RenameField(
            model_name="orderitem",
            old_name="price",
            new_name="unit_price",
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="order_items",
                to="menu.fooditem",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="product_name",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(
            snapshot_order_items,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="order",
            name="items",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="cartitem",
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="order.order",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="unit_price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0.00"))
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                condition=models.Q(("quantity__gte", 1)),
                name="order_item_quantity_at_least_one",
            ),
        ),
    ]
