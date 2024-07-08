from django.shortcuts import redirect, render
from .models import *
from admin_side import views 
from category.models import category as Category
from banner.models import Banner
from django.db.models import Q
from products.models import Products

# Create your views here.


def category_list(request):
    if 'email' in request.session:
        search_query = request.GET.get('search', '')
        cat=category.objects.all()
        if search_query:
            cat = cat.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category_offer_description__icontains=search_query) 
                
            )
        context={
            'cat':cat,
            'search_query': search_query,
            }
        return render(request, 'admin_side/category.html', context)
    return render(request,'admin_side/admin_login.html')
    
    
def add_category(request):
    
    if 'email' in request.session:
        if request.method == 'POST':
            name=request.POST.get('name')
            description=request.POST.get('description')
            image = request.FILES.get('image')
            category_offer_description=request.POST.get('category_offer_description')
            category_offer=request.POST.get('category_offer')
            
            new_category=category(
                name=name,
                description=description,
                image=image,
                category_offer_description=category_offer_description,
                category_offer=category_offer
                )
            new_category.save()
            return redirect('category_management')
    
        return render(request, 'admin_side/add_category.html')
    return render(request,'admin_side/admin_login.html')
    
def delete_category(request,id):
    if 'email' in request.session:
        cat=category.objects.get(id=id)
        cat.delete()
        return redirect('category_management')
    return render(request,'admin_side/admin_login.html')
    


def edit_category(request,id):
    if 'email' in request.session:
        cat=category.objects.get(id=id)
        if request.method=='POST':
            name=request.POST.get('name')
            description=request.POST.get('description')
            image = request.FILES.get('image')
            category_offer_description=request.POST.get('category_offer_description')
            category_offer=request.POST.get('category_offer')
            cat.name=name
            cat.description=description
            cat.category_offer=category_offer
            if image:
                cat.image=image
            cat.category_offer_description=category_offer_description  
            cat.save() 
          
            
            return redirect('category_management')
            
        context={
            'cat':cat,
            }    
        return render(request, 'admin_side/edit_category.html',context)
    return render(request,'admin_side/admin_login.html')
    



def block_category(request,id):
    if 'email' in request.session:
        cat=category.objects.get(id=id)
        cat.is_active=False
        cat.save()
        return redirect('category_management')
    
def unblock_category(request,id):
    if 'email' in request.session:
        cat=category.objects.get(id=id)
        cat.is_active=True
        cat.save()
        return redirect('category_management')
    else:
        return render(request,'admin_side/admin_login.html')
        
def add_brand(request):
    if 'email' in request.session:
        if request.method == 'POST':
            brand=request.POST.get('brand')
            logo=request.FILES.get('logo')
            new_brand=Brand.objects.create(brand_name=brand,logo=logo)
            return redirect('category_management')
        return render(request, 'admin_side/add_brand.html')
    else:
        return render(request,'admin_side/admin_login.html')
    

    
def banner_management(request):
    if 'email' in request.session:
        banner=Banner.objects.all()
    
        context={
            'banner': banner,
        }
        return render(request, 'admin_side/banner_management.html',context)
    else:
        return render(request,'admin_side/admin_login.html')

def add_banner(request):
    if 'email' in request.session:
        categories = Category.objects.all()
        context = {
            'categories': categories
        }
        if request.method == 'POST':
            title = request.POST.get('title')
            cat_id = request.POST.get('category')
            image = request.FILES.get('image')
            price=request.POST.get('price')
            offer_details = request.POST.get('offer_details')
            
            # Check if all required data is provided
            if title and category and image:
                cat=Category.objects.get(id=cat_id)
                banner = Banner.objects.create(title=title, category=cat, image=image,price=price,offer_details=offer_details)
                return redirect('banner_management')
            else:
                # Handle invalid or incomplete form submission
                context['error_message'] = "Please provide all required information."
                
        # If the request is not a POST request or form submission failed, render the form again
        return render(request, 'admin_side/add_banner.html', context)
    # If user is not logged in, redirect them to login page or handle as appropriate
    return redirect('admin_login')



def update_banner(request,id):
    if 'email' in request.session:
        banner=Banner.objects.get(id=id)
        categories = Category.objects.all()
        
        context={
            'banner':banner,
            'categories':categories,
        }
        if request.method=='POST':
            title=request.POST.get('title')
            cat_id=request.POST.get('category')
            image=request.POST.get('image')
            price=request.POST.get('price')
            offer_details=request.POST.get('offer_details')
        
        
            banner.title=title
            banner.category=Category.objects.get(id=cat_id)
            banner.image=image
            banner.price=price
            banner.offer_details=offer_details
        
            banner.save()
            return redirect('banner_management')
        
        return render(request, 'admin_side/update_banner.html',context)
    return redirect('admin_login')  
    
def delete_banner(request,id):
     if 'email' in request.session:
        banner= Banner.objects.get(id=id)
        banner.delete()
        return redirect('banner_management')  
    
    
def block_banner(request,id):
    if 'email' in request.session:
        banner= Banner.objects.get(id=id)
        banner.is_active=False
        banner.save()
        return redirect('banner_management')  

def unblock_banner(request,id):
    if 'email' in request.session:
        banner= Banner.objects.get(id=id)
        banner.is_active=True
        banner.save()
        return redirect('banner_management')  
    
def inventory(request):
    stock_items=Products.objects.all()
    
    context={
        'stock_items': stock_items
    }
    return render(request, 'admin_side/inventory.html',context)