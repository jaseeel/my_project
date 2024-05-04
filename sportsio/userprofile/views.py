from django.shortcuts import render, get_object_or_404
from .models import *
from admin_side.views import *
from django.http import JsonResponse
# Create your views here.

#_____________Account Page ________________

def user_profile(request):
    user=request.user
    if user.is_authenticated:
        addresses=address.objects.filter(username=user)
        context={
             'user':user,
             'address':addresses,
         }
        return render(request,"user_side/user_profile.html",context)
    else:
        return redirect('login')


#__________________Add Address_______________

def add_address(request):
    user = request.user

    if request.method == "POST":
        addresses=request.POST.get("address")
        house_name = request.POST.get("house_name")
        street = request.POST.get("street")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip")

        # Create a new Address object associated with the current user
        address.objects.create(
            username=user,
            address=addresses,
            house_name=house_name,
            street=street,
            city=city,
            state=state,
            zipcode=zip_code,
        )

        # Update the addresses queryset to include the new address
        return redirect("user_profile:user_profile")
    return render(request, "user_side/add_address.html")


#_______________ Edit Address____________

def edit_address(request, id):
    addy=address.objects.get(id=id)
    context={
        'addy':addy
    }
    if request.method == "POST":
        addy.address=request.POST.get("address")
        addy.house_name = request.POST.get("house_name")
        addy.street = request.POST.get("street")
        addy.city = request.POST.get("city")
        addy.state = request.POST.get("state")
        addy.zip_code = request.POST.get("zip")
    
        addy.save()
        return redirect('user_profile:user_profile')
    return render(request,"user_side/edit_address.html",context)

#____________Delete Address_____________

def delete_address(request,id):
    addy = get_object_or_404(address, id=id)
    addy.delete()
    return redirect('user_profile:user_profile')
    

# ADD TO CART
        
def add_tocart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            prod_qty = int(request.POST.get('product_qty'))
            product_check = Products.objects.get(id=prod_id)
           
            if product_check:
                if Cart.objects.filter(user=request.user, product_id=prod_id).exists():
                    prod_qty += 1
                else:
                    
                    if product_check.stock_count >= prod_qty:
                        # print(prod_id)
                        # print(prod_qty)
                        val = Products.objects.get(id=prod_id)
                        
                        Cart.objects.create(
                            user=request.user,
                            product_id=val,
                            product_qty=prod_qty
                        )
                        return JsonResponse({'status': "Product Added Successfully"})
                    else:
                        return JsonResponse({'status': "Limited stocks left"})
            else:
                return JsonResponse({'status': "Product not found"})
        else:
            return JsonResponse({"status": "User must be logged in"})
    return redirect('/')


# ______________Cart_view_________
def cart_view(request):
    carts=Cart.objects.all()
    context={
        'carts':carts
    }
    return render(request,"user_side/cart_view.html")
