from django.shortcuts import render,HttpResponse,redirect
from products.models import Products
# Create your views here.


def inventory(request):
    stock_items=Products.objects.all()
    
    context={
        'stock_items': stock_items
    }
    return render(request, 'admin_side/inventory.html',context)

def update_stock(request):
        if request.method == 'POST':
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity', 0)
            print("Product ID received:", product_id)

        # Ensure product_id is provided
            if not product_id:
                return HttpResponse("Product ID is missing", status=400)

        # Validate product_id
            try:
                product = Products.objects.get(pk=product_id)
            except Products.DoesNotExist:
                return HttpResponse("Product not found", status=404)
            else:
            # Validate quantity
                try:
                    quantity = int(quantity)
                except ValueError:
                    return HttpResponse("Invalid quantity", status=400)

            # Update stock count
                product.stock_count = quantity
                product.save()

                return redirect('inventory')  # Redirect to the inventory page after successful update

    # Return an HttpResponse with an error message if accessed via GET or any other method
            return HttpResponse("Method not allowed", status=405)
        return render(request,'admin_side/admin_login.html')