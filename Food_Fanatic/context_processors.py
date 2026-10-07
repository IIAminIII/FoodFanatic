"""Template context available on every page."""

from django.db.models import Sum


def cart_count(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"cart_count": 0}

    from menu.models import CartItem

    total = (
        CartItem.objects.filter(user=request.user)
        .aggregate(total=Sum("quantity"))
        .get("total")
    )
    return {"cart_count": total or 0}
