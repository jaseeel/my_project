from django.shortcuts import render,redirect
from django.db.models import Q
from category.models import category,Brand
from banner.models import Banner
from category.views import views
from products.models import Products, ProductImage
from django.utils import timezone
from datetime import timedelta
from userprofile.models import Cart
from admin_side.views import *



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
    banner=Banner.objects.filter(is_active=True)
    products=Products.objects.filter(is_active=True,status='In Stock')
    brand=Brand.objects.all()
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_products = Products.objects.filter(created_date__gte=seven_days_ago,is_active=True,status='In Stock')

    
    context={
        'Category': Category,
        'products': products,
        'brand': brand,
        'banner' : banner,
        'recent_products' : recent_products,

    }

    
    
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
    product=Products.objects.filter(is_active=True)
            #Navbar Cart Items 
    cart_count=Cart.objects.filter(user=request.user).count()
    cart = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.offer_price * item.product_quantity for item in cart)
    context={
        'product':product,
        'cart_count':cart_count,
        'total_price':total_price
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
            # Include conditions for product title, category name, and brand name
            q_objects |= Q(title__icontains=term) | Q(category__name__icontains=term) | Q(brand__brand_name__icontains=term)

        # Filter products based on the constructed query
        product = Products.objects.filter(q_objects,is_active=True).distinct()
        advnced=True
        context = {
            'product': product,
            'advnced':advnced
        }
        return render(request, 'user_side/product_list.html', context)

    return redirect('home')

#________________SORT_________________

def sort(request):
    product = Products.objects.filter(is_active=True).order_by('-id')  # Retrieve all products initially

    # Sorting logic
    sort_by = request.GET.get('sort_by')
    if sort_by:
        if sort_by == 'price-':
            product = product.order_by('offer_price')
        elif sort_by == 'price+':
            product = product.order_by('-offer_price')
        elif sort_by == 'a-z':
            product = product.order_by('title')
        elif sort_by == 'z-a':
            product = product.order_by('-title')

    return render(request, 'user_side/product_list.html', {'product': product})
        
        
# ADD TO CART VIEWS 


