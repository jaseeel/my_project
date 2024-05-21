from datetime import timezone
from django.db import models
from products.models import Products
# Create your models here.

   
   
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=20
    )  # 'percentage', 'fixed_amount', 'free_shipping', etc.
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    max_uses = models.IntegerField()
    used_count = models.IntegerField(default=0)

    def is_valid(self, order_total):
        return (
            timezone.now().date() <= self.expiration_date
            and self.used_count < self.max_uses
            and order_total >= self.min_order_value
        )

    def apply_discount(self, order_total):
        if self.discount_type == "percentage":
            return order_total * (1 - self.discount_value / 100)
        elif self.discount_type == "fixed_amount":
            return order_total - self.discount_value
        else:
            return order_total