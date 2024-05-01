from django.db import models
from products.models import Products
# Create your models here.
class Stock(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Stock for {self.product.title}"