from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def prepare_existing_data(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    CartItem = apps.get_model("menu", "CartItem")
    Review = apps.get_model("menu", "Review")

    used_slugs = set()
    for category in Category.objects.order_by("pk"):
        base = slugify(category.slug or category.name) or f"category-{category.pk}"
        candidate = base
        suffix = 2
        while candidate in used_slugs:
            candidate = f"{base}-{suffix}"
            suffix += 1
        if category.slug != candidate:
            category.slug = candidate
            category.save(update_fields=("slug",))
        used_slugs.add(candidate)

    seen_cart_items = {}
    for cart_item in CartItem.objects.select_related("product").order_by("pk"):
        key = (cart_item.user_id, cart_item.product_id)
        if cart_item.unit_price is None:
            cart_item.unit_price = cart_item.product.price
        if key in seen_cart_items:
            primary = seen_cart_items[key]
            primary.quantity += cart_item.quantity
            primary.save(update_fields=("quantity",))
            cart_item.delete()
        else:
            cart_item.save(update_fields=("unit_price",))
            seen_cart_items[key] = cart_item

    for review in Review.objects.all():
        raw_rating = str(review.rating).strip()
        if raw_rating.isdigit():
            value = int(raw_rating)
        else:
            value = raw_rating.count("\u2b50") or raw_rating.count("\u2605")
            if not value and len(raw_rating) % 3 == 0:
                value = len(raw_rating) // 3
        review.rating_value = min(max(value or 5, 1), 5)
        review.save(update_fields=("rating_value",))


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0004_fooditem_active_fooditem_discount_price_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="category",
            options={"ordering": ("name",), "verbose_name_plural": "categories"},
        ),
        migrations.AlterModelOptions(
            name="fooditem",
            options={"ordering": ("title",)},
        ),
        migrations.AlterModelOptions(
            name="cartitem",
            options={"ordering": ("id",)},
        ),
        migrations.AlterModelOptions(
            name="review",
            options={"ordering": ("-created",)},
        ),
        migrations.AlterField(
            model_name="fooditem",
            name="title",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="fooditem",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0.01"))
                ],
            ),
        ),
        migrations.AlterField(
            model_name="fooditem",
            name="discount_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0.01"))
                ],
            ),
        ),
        migrations.AlterField(
            model_name="fooditem",
            name="category",
            field=models.ManyToManyField(
                related_name="food_items",
                to="menu.category",
            ),
        ),
        migrations.AlterField(
            model_name="fooditem",
            name="active",
            field=models.BooleanField(
                default=False,
                help_text="Enable the discount, subject to its start and end dates.",
            ),
        ),
        migrations.AddField(
            model_name="fooditem",
            name="is_available",
            field=models.BooleanField(default=True),
        ),
        migrations.RenameField(
            model_name="cartitem",
            old_name="price",
            new_name="unit_price",
        ),
        migrations.AddField(
            model_name="review",
            name="rating_value",
            field=models.PositiveSmallIntegerField(default=5),
            preserve_default=False,
        ),
        migrations.RunPython(
            prepare_existing_data,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AddConstraint(
            model_name="cartitem",
            constraint=models.UniqueConstraint(
                fields=("user", "product"),
                name="unique_cart_product_per_user",
            ),
        ),
        migrations.AddConstraint(
            model_name="cartitem",
            constraint=models.CheckConstraint(
                condition=models.Q(("quantity__gte", 1)),
                name="cart_quantity_at_least_one",
            ),
        ),
        migrations.RemoveField(
            model_name="review",
            name="rating",
        ),
        migrations.RenameField(
            model_name="review",
            old_name="rating_value",
            new_name="rating",
        ),
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="menu.fooditem",
            ),
        ),
    ]
