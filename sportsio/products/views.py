from django.shortcuts import redirect, render
from .models import Products
from .models import ProductImage as ProductImage
from category.models import category as Category  
from category.models import Brand as Brand
from admin_side import views
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


# Create your views here.
#_______PRODUCT__MANAGEMENT__VIEW____

def product_view(request):
    if 'email' in request.session:
        search_query = request.GET.get('search', '')
        products = Products.objects.all()
        #Search query
        if search_query:
            products = products.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(brand__brand_name__icontains=search_query)
            )

        context = {
            'products': products,
            'search_query': search_query,
        }
        return render(request, 'admin_side/product_management.html', context)



#_______ ADD_PRODUCT_______
def add_product(request):
    if 'email' in request.session:
        status_choices = Products.Status_choices  # Use the model's choices
        categories = Category.objects.filter(is_active=True)
        brands = Brand.objects.all()
        
        context = {
            'categories': categories,
            'status_choices': status_choices,
            'brands': brands,
        }

        if request.method == 'POST':
            # Retrieve form data
            title = request.POST.get('title')
            category_id = request.POST.get('category')
            description = request.POST.get('description')
            price = request.POST.get('price')
            brand_id = request.POST.get('brand')
            status = request.POST.get('status')
            stock_count = request.POST.get('stock_count')
            image= request.FILES.get('image') 
            weight = request.POST.get('weight')
            featured = request.POST.get('featured')=='on'
            offer_price = request.POST.get('offer_price')
            if offer_price :
                try:
                    offer_price = float(offer_price)
                except ValueError:
                    offer_price = price

            # Retrieve category and brand objects
            category = Category.objects.get(id=category_id)
            
            if category.category_offer:
                cat_offer=int(price)*(category.category_offer/100)
                offer_price=int(price) - cat_offer
            
            brand = Brand.objects.get(id=brand_id)
            
          
            # Create Products object
            product = Products.objects.create(
                title=title,
                category=category,
                description=description,
                price=price,
                brand=brand,
                status=status,
                stock_count=stock_count,
                image=image,
                weight=weight,
                featured=featured,
                offer_price=offer_price
            )
            if request.FILES.getlist('images'):
                for img in request.FILES.getlist('images'):
                    ProductImage.objects.create(product=product, image=img)

            # Redirect after successful creation
            return redirect('product_management')

        return render(request, 'admin_side/add_product.html', context)
    return render(request, 'admin_side/admin_login.html')

def update_product(request, id):
    if 'email' in request.session: 
        product = Products.objects.get(id=id)
        status_choices = Products.Status_choices
        categories = Category.objects.all()
        brand = Brand.objects.all()
        context = {
            'brand': brand,
            'categories': categories,
            'status_choices': status_choices,
            'product': product,
        }
        if request.method == 'POST':
            title = request.POST.get('title')
            cat_id = request.POST.get('category')
            description = request.POST.get('description')
            status = request.POST.get('status')
            price = request.POST.get('price')
            brand_id = request.POST.get('brand')
            image = request.FILES.get('image')  # Get the uploaded image
            product_details = request.POST.get('product_details')
            stock_count = request.POST.get('stock_count')
            weight = request.POST.get('weight')
            featured = request.POST.get('featured')=='on'
            offer_price = request.POST.get('offer_price')
            if offer_price:
                try:
                    offer_price = int(offer_price)
                except ValueError:
                    offer_price = price
            # Retrieve category and brand objects
            category = Category.objects.get(id=cat_id)
            
            if category.category_offer:
                cat_offer=int(price)*(category.category_offer/100)
                offer_price=int(price) - cat_offer
            # Update product fields
            product.title = title
            product.category = Category.objects.get(id=cat_id)
            product.description = description
            product.price = price
            product.brand = Brand.objects.get(id=brand_id)
            # Only assign the new image if one is provided
            if image:
                product.image = image
            product.stock_count = stock_count  
            product.status = status
            product.weight = weight
            product.featured = featured
            product.product_details=product_details
            product.offer_price=offer_price

            # Handle existing and new additional images
            existing_images = product.additional_images.all()
            new_images = request.FILES.getlist('images')

            # Only delete existing images if new images are uploaded
            if new_images:
                for img in existing_images:
                    img.delete()
            # Save product
            product.save()

            # Save newly uploaded additional images
            for image in new_images:
                ProductImage.objects.create(product=product, image=image)

            return redirect('product_management')

        return render(request, 'admin_side/product_update.html', context)
    return redirect('admin_login')



def block_product(request,id):
    product=Products.objects.get(id=id)
    product.is_active=False
    product.save()
   
    return redirect('product_management')



def unblock_product(request,id):
    product=Products.objects.get(id=id)
    product.is_active=True
    product.save()
    print(product.is_active)
    return redirect('product_management')
    
def delete_product(request,id):
    product=Products.objects.get(id=id)
    product.delete()
    return redirect('product_management')