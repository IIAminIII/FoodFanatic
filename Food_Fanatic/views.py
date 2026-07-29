import logging

from django.conf import settings
from django.db import connection
from django.shortcuts import get_object_or_404, render

from menu.models import Category, FoodItem


logger = logging.getLogger(__name__)


def home(request, category_slug=None):
    food_items = FoodItem.objects.filter(is_available=True).prefetch_related("category")
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        food_items = food_items.filter(category=category)

    logger.info(
        "Menu request backend=%s host=%s available_items=%s",
        connection.vendor,
        settings.DATABASES["default"].get("HOST", ""),
        food_items.count(),
    )

    return render(
        request,
        "home.html",
        {
            "data": food_items,
            "categories": Category.objects.all(),
        },
    )
