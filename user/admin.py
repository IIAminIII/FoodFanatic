from django.contrib import admin

from .models import AccountModel


@admin.register(AccountModel)
class AccountModelAdmin(admin.ModelAdmin):
    list_display = ("user", "is_activated")
    list_filter = ("is_activated",)
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
    readonly_fields = ("email_token",)
