from django.urls import path
from . import views
urlpatterns = [
    path("placeorder/", views.place_order, name="placeorder"),
    path(
        "order_details/<int:order_id>/",
        views.order_details,
        name="order_details",
    ),
    path(
        "orderhistory/",
        views.OrderHistoryView.as_view(),
        name="orderhistory",
    ),
    path("cancel/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("manage/", views.manage_orders, name="manage_orders"),
    path(
        "manage/<int:order_id>/update/",
        views.update_order_status,
        name="update_order_status",
    ),
]
