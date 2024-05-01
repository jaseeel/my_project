from django import forms
from .models import Products
 
class ImageForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ('image',) 