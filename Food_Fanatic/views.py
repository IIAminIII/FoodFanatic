from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from menu.models import Category, FoodItem


def healthz(request):
    """Report whether the app can reach its database.

    Exists so an unreachable production database (an expired free-tier
    instance, a paused project, a bad DATABASE_URL) is diagnosable from a
    browser instead of appearing as a blank 500 on every page.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as exc:  # pragma: no cover - exercised via mock in tests
        return JsonResponse(
            {
                "status": "error",
                "database": f"{type(exc).__name__}: {exc}",
                "hint": (
                    "The database is unreachable. Check that the PostgreSQL "
                    "instance still exists and that DATABASE_URL/POSTGRES_URL "
                    "in the deployment environment points at it."
                ),
            },
            status=503,
        )
    return JsonResponse({"status": "ok", "database": "ok"})


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
