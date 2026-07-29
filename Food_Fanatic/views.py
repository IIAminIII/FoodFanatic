from django.shortcuts import get_object_or_404, render

from menu.models import Category, FoodItem


def home(request, category_slug=None):
    food_items = FoodItem.objects.filter(is_available=True).prefetch_related("category")
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        food_items = food_items.filter(category=category)

    return render(
        request,
        "home.html",
        {
            "data": food_items,
            "categories": Category.objects.all(),
        },
    )
