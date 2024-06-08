from datetime import timezone
from django.db import models
from products.models import Products
from admin_side.models import CustomUser
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


#______________Save Wallet Transactions___________________

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('P', 'Payment'),  # New transaction type for payments
        ('R', 'Refund'),
        # Add other types if needed
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"