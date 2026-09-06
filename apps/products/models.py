from django.db import models
from apps.common.models import SoftDeleteModel


class Product(SoftDeleteModel):
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_quentity = models.PositiveIntegerField(default=0)
    product_category = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_name} - {self.product_category}" 
