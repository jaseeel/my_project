from django.db import models
from category.models import category
# Create your models here.
class Banner(models.Model):
    title = models.CharField(max_length=255,unique=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banner_image')
    offer_details = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title