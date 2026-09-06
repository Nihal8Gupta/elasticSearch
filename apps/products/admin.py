from django.contrib import admin
from .models import Product
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_price', 'product_quentity', 'product_category')
    search_fields = ('product_name', 'product_category')