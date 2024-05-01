from django.shortcuts import redirect, render
from .models import Products
from .models import ProductImage as ProductImage
from category.models import category as Category  
from category.models import Brand as Brand
from admin_side import views
from django.utils import timezone
import base64
from datetime import timedelta
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


# Create your views here.
def product_view(request):
    products=Products.objects.all()

    

    context={
        'products': products,
        
        
    }
    return render(request, 'admin_side/product_management.html',context)

def add_product(request):
    if 'email' in request.session:
        status_choices = Products.Status_choices  # Use the model's choices
        categories = Category.objects.all()
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
            if offer_price:
                try:
                    offer_price = int(offer_price)
                except ValueError:
                    offer_price = price

            

            # Retrieve category and brand objects
            category = Category.objects.get(id=category_id)
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
            product_details = request.POST.get('product_details')
            stock_count = request.POST.get('stock_count')
            weight = request.POST.get('weight')
            featured = request.POST.get('featured')=='on'
            print(featured)
            offer_price = request.POST.get('offer_price')
            if offer_price:
                try:
                    offer_price = int(offer_price)
                except ValueError:
                    offer_price = price
            # Update product fields
            product.title = title
            product.category = Category.objects.get(id=cat_id)
            product.description = description
            product.price = price
            product.brand = Brand.objects.get(id=brand_id)
            product.stock_count = stock_count  
            product.status = status
            product.weight = weight
            product.featured = featured
            product.product_details=product_details
            product.offer_price=offer_price


            # Handle existing additional images
            existing_images = product.additional_images.all()

            # Handle uploaded additional images
            new_images = request.FILES.getlist('images')

            # Save product
            product.save()

            # Save newly uploaded additional images
            for image in new_images:
                ProductImage.objects.create(product=product, image=image)

            return redirect('product_management')

        return render(request, 'admin_side/product_update.html', context)
    return render(request, 'admin_side/admin_login.html')


def block_product(request,id):
    product=Products.objects.get(id=id)
    product.is_active=False
    product.save()
    print("block")
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