from django.shortcuts import render
from category.models import category,Brand
from banner.models import Banner
from category.views import views
from products.models import Products, ProductImage
from django.utils import timezone
from datetime import timedelta

# Create your views here.
def base(request):
    Category=category.objects.filter(is_active=True)[:5]
    products=Products.objects.filter(is_active=True,status='In Stock')
    brand=Brand.objects.all()
    context={
        'Category': Category,
        'products': products,
        'brand': brand,
    }
    return render(request, 'user_side/base.html',context)

def home(request):
    print("This is printing from home page")
    Category=category.objects.filter(is_active=True)[:5]
    banner=Banner.objects.all()
    products=Products.objects.filter(is_active=True,status='In Stock')
    brand=Brand.objects.all()
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_products = Products.objects.filter(created_date__gte=seven_days_ago,is_active=True,status='In Stock')
    context={
        'Category': Category,
        'products': products,
        'brand': brand,
        'banner' : banner,
        'recent_products' : recent_products
    }
    print(recent_products.values())
    
    
    return render(request,'user_side/main.html',context)

def user_product_view(request, id):
    product = Products.objects.get(id=id)
    related_products = Products.objects.filter(category=product.category).exclude(id=id)
    product_images =ProductImage.objects.filter(product=product)

    context = {
        'product_images': product_images,
        'product': product,
        'related_products':related_products
    }

    return render(request, 'user_side/product-view.html', context)

#def banner_view(request):
    # laptop_banner=category.objects.get(name='Laptop')
    # Tvandbanner=category.objects.get(name='Tv and audio')
    # smartphonebanner=category.objects.get(name='smartphone')
    # wearablesbanner=category.objects.get(name='Wearables')
    
    # allban=Banner.objects.filter(is_active=True)
    # lapban=Banner.objects.filter(category=laptop_banner,is_active=True)       
    # tvban=Banner.objects.filter(category=Tvandbanner,is_active=True)
    # smartphoneban=Banner.objects.filter(category=smartphonebanner,is_active=True)
    # wearablesbanner=Banner.objects.filter(category=wearablesbanner,is_active=True)
    
    # context={
    #     'allban':allban,
    #     'lapban':lapban,
    #     'tvban':tvban,
    #     'wearablesbanner':wearablesbanner,
    #     'smartphoneban':smartphoneban, 
        
    # }
    # banner=Banner.objects.all()
    #context ={
     #   'banner' : banner
    #}
    
    #return render(request, 'user_side/product-view.html', context)