from django.contrib import admin

from .models import CartItem, Category, FoodItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "discount_price",
        "active",
        "is_available",
    )
    list_filter = ("is_available", "active", "category")
    search_fields = ("title", "description")
    filter_horizontal = ("category",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "unit_price")
    list_select_related = ("user", "product")
    search_fields = ("user__username", "product__title")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("item", "reviewer", "rating", "created")
    list_filter = ("rating", "created")
    list_select_related = ("item", "reviewer")
    search_fields = ("item__title", "reviewer__username", "body")
