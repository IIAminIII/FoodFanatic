from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "quantity", "unit_price", "line_total")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "placed_at")
    list_filter = ("status", "placed_at")
    search_fields = ("id", "user__username", "user__email")
    list_select_related = ("user",)
    readonly_fields = ("user", "total_amount", "placed_at")
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "quantity", "unit_price", "line_total")
    list_select_related = ("order", "product")
    readonly_fields = ("order", "product", "product_name", "quantity", "unit_price")

    def has_add_permission(self, request):
        return False
