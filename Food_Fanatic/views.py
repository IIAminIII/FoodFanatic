from django.db import connection
from django.db.models import Avg, Count, Q
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


def _menu_queryset():
    return (
        FoodItem.objects.filter(is_available=True)
        .prefetch_related("category")
        .annotate(
            avg_rating=Avg("reviews__rating"),
            review_count=Count("reviews", distinct=True),
        )
    )


def home(request, category_slug=None):
    food_items = _menu_queryset()

    active_category = None
    if category_slug is not None:
        active_category = get_object_or_404(Category, slug=category_slug)
        food_items = food_items.filter(category=active_category)

    query = request.GET.get("q", "").strip()
    if query:
        food_items = food_items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Discount dates are checked in Python because is_discount_active owns
    # that logic; the queryset narrows to plausible candidates first.
    offers = [
        item
        for item in _menu_queryset().filter(active=True, discount_price__isnull=False)
        if item.is_discount_active
    ]

    return render(
        request,
        "home.html",
        {
            "data": food_items,
            "categories": Category.objects.all(),
            "offers": offers,
            "query": query,
            "active_category": active_category,
        },
    )
