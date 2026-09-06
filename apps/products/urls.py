from django.urls import path

from . import views


app_name = "products"

urlpatterns = [
    path("", views.product_search, name="search"),
    path("suggestions/", views.product_suggestions, name="suggestions"),
    path("<int:product_id>/", views.product_detail, name="detail"),
]
