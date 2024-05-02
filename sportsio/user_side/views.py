from django.shortcuts import render,redirect
from django.db.models import Q
from category.models import category,Brand
from banner.models import Banner
from category.views import views
from products.models import Products, ProductImage
from django.utils import timezone
from datetime import timedelta

# Create your views here.

#___________________ Base Views_____________________

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

#___________________Main Page_______________

def home(request):
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

#________________ Single Product View_____________ 

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

def product_list(request):
    product=Products.objects.all()
    context={
        'product':product
    }
    return render(request,"user_side/product_list.html",context)

#___________________Search________________

def product_search(request):
    if request.method == "POST":
        searched = request.POST.get('searched')

        # Split the searched term into individual words
        search_terms = searched.split()

        # Initialize an empty Q object to build the query dynamically
        q_objects = Q()

        # Iterate through each search term and construct the query
        for term in search_terms:
            q_objects |= Q(product__model__icontains=term) | Q(product__brand__name__icontains=term)

        # Filter products based on the constructed query
        products = Products.objects.filter(q_objects).distinct()

        context = {
            'products': products,
        }
        return render(request, 'user_side/product_list.html', context)

    return redirect('home')
