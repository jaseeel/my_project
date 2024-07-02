from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.db.models import Q,Avg, F
from category.models import category,Brand
from banner.models import Banner
from category.views import views
from django.db.models import Count
from products.models import Products, ProductImage,product_review
from django.utils import timezone
from datetime import timedelta
from userprofile.models import Cart
from admin_side.views import *
from django.core.paginator import Paginator



# Create your views here.

#___________________ Base Views_____________________

def base(request):
    Category=category.objects.filter(is_active=True)[:5]
    products=Products.objects.filter(is_active=True,status='In Stock')
    brand=Brand.objects.all()
    if request.user.is_authenticated:
        cart_count=Cart.objects.filter(user=request.user).count()
        return JsonResponse({"cart_count":cart_count})
    context={
        'Category': Category,
        'products': products,
        'brand': brand,

    }
    return render(request, 'user_side/base.html',context)

#___________________Main Page_______________

def home(request):
    Category=category.objects.filter(is_active=True)
    banner=Banner.objects.filter(is_active=True)
    products=Products.objects.filter(is_active=True,status='In Stock')
    brand=Brand.objects.all()
    seven_days_ago = timezone.now() - timedelta(days=30)
    recent_products = Products.objects.filter(created_date__gte=seven_days_ago,is_active=True,status='In Stock')
    for rev in products :
        average_stars=product_review.objects.filter(Title_id=rev.id).aggregate(Avg('stars'))
        if average_stars['stars__avg']:
            rev.stars=int(average_stars["stars__avg"])
            rev.save()
    for rev in recent_products :
        average_stars=product_review.objects.filter(Title_id=rev.id).aggregate(Avg('stars'))
        if average_stars['stars__avg']:
            rev.stars=int(average_stars["stars__avg"])
            rev.save()
    
    
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
    if request.user.is_authenticated:
        email=request.user.email
        if request.method == "POST":
           user=request.POST.get('con_email')
           stars=request.POST.get('star-rating')
           Title=request.POST.get('prodid')
           review=request.POST.get('con_message')
           user_rev=CustomUser.objects.get(email=user)
           product_rev=Products.objects.get(id=Title)
           review=product_review.objects.create(
               user=user_rev,
               stars=stars,
               Title=product_rev,
               review=review,
           )
           messages.success(request,"Review Submitted")

    rating=product_review.objects.filter(Title_id=id)
    rating_count=product_review.objects.filter(Title_id=id).count()
    average_stars=product_review.objects.filter(Title_id=id).aggregate(Avg('stars'))
    if average_stars['stars__avg']:
        product.stars=int(average_stars["stars__avg"])
        product.save()
        
        

    context = {
        'product_images': product_images,
        'product': product,
        'related_products':related_products,
        'email':email,
        'rating':rating,
        'rating_count':rating_count,

    }

    return render(request, 'user_side/product-view.html', context)

def product_list(request):
    product=Products.objects.filter(is_active=True)
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
        elif sort_by == 'rating+':
            product=Products.objects.annotate(avg_stars=Avg(F('reviews__stars'), output_field=models.FloatField())).order_by('-avg_stars')
            
        elif sort_by == 'rating-':
            product = Products.objects.annotate(avg_stars=Avg(F('reviews__stars'), output_field=models.FloatField())).order_by('avg_stars')
        
        for rev in product:
            average_stars=product_review.objects.filter(Title_id=rev.id).aggregate(Avg('stars'))
            if average_stars['stars__avg']:
                rev.stars=int(average_stars["stars__avg"])
                rev.save()
    # Paginator
    items_per_page = 9
    paginator = Paginator(product, items_per_page)
    page_number = request.GET.get('page')
    print(page_number)
    page_obj = paginator.get_page(page_number)
   

    return render(request, 'user_side/product_list.html', {'product': page_obj,'sort_by':sort_by})

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


#________ Shop by Category________

def shop_by_cat(request):
    category_list = category.objects.filter(is_active=True).annotate(product_count=Count('category_name'))
    cat_id=request.GET.get('cat_id')
    print("hiii",cat_id)
    if cat_id:
        cat = category.objects.get(id=cat_id)
        product_list=Products.objects.filter(is_active=True,category=cat)
        print("products",product_list)
    else:
        product_list=Products.objects.filter(is_active=True)
    items_per_page = 9
    paginator = Paginator(product_list, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={
        "category_list":category_list,
        "product_list":page_obj
    }

    
    return render(request,"user_side/shop_category.html",context)
        
        
        
        
        



