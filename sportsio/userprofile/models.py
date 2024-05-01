from django.db import models
from django.utils import timezone
from django.db import models
from admin_side.models import CustomUser
# Create your models here.



# Address Details
class address(models.Model):
    username= models.ForeignKey(CustomUser, related_name="user_name",on_delete=models.CASCADE)
    house_name=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    city=models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    