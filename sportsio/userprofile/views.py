from django.shortcuts import render, get_object_or_404

from inventory.models import Coupon
from .models import *
from admin_side.models import CustomUser
from admin_side.views import *
from products.models import Products
from django.http import JsonResponse
from django.db.models import F
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.decorators import login_required

# Create your views here.

#_____________Account Page ________________

def user_profile(request):
    user=request.user
    if user.is_authenticated:
        addresses=address.objects.filter(username=user)
        reset_user=CustomUser.objects.filter(username=user)
 
        # Fetch orders related to the current user
        user_orders = Order.objects.filter(user=request.user).exclude(status='Cancelled')
        context={
             'user':user,
             'address':addresses,
             "reset_user":reset_user,
             "orders": user_orders,
         }
        return render(request,"user_side/user_profile.html",context)
    else:
        return redirect('home')


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
    

#________ADD TO CART________
        
from django.db.models import F

def add_tocart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            prod_id = int(request.POST.get('product_id'))
            prod_qty = int(request.POST.get('product_qty'))
            product_check = Products.objects.get(id=prod_id)
           
            if product_check:
                if Cart.objects.filter(user=request.user, product=prod_id).exists():
                    # Use update() to increment the product_qty of the existing cart item
                    Cart.objects.filter(user=request.user, product=prod_id).update(product_quantity=F('product_quantity') + prod_qty)
                    
                    return JsonResponse({'status': "Cart Updated Successfully"})
                else:
                    if product_check.stock_count >= prod_qty:
                        val = Products.objects.get(id=prod_id)

                        Cart.objects.create(
                            user=request.user,
                            product=val,
                            product_quantity=prod_qty
                            )
                        return JsonResponse({'status': "Product Added Successfully"})
                    else:
                        return JsonResponse({'status': "Limited stocks left"})
            else:
                return JsonResponse({'status': "Product not found"})
        else:
            # Use Django's messaging framework to inform the user
            messages.error(request, "Login Required")
            # Redirect the user to the login page
            return redirect('login')
    return redirect('/')


# ______________Cart_view_________

def cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access Cart.")
        return redirect("login")
    # Retrieve the current user's cart items
    cart = Cart.objects.filter(user=request.user)
    cart_count=Cart.objects.filter(user=request.user).count()
    total_price = sum(item.product.offer_price * item.product_quantity for item in cart)
    print(total_price)
    Coupon_discount=0

    # Calculate stock_count_plus_one for each product in the cart
    max_stock_count_plus_one = Products.objects.aggregate(Max("stock_count"))[
        "stock_count__max"
    ]
    # If there are no products or if the stock count is not available, default to 1
    stock_count_plus_one = max_stock_count_plus_one or 1

    if request.method == "POST":
       print("message sent here")
       coupon_code = request.POST.get("coupon_code")
       try:
           coupon = Coupon.objects.get(code=coupon_code)
           if coupon.discount_type == "percentage":
               Coupon_discount = (total_price * coupon.discount_value) / 100
           elif coupon.discount_type == "fixed_amount":
               Coupon_discount = coupon.discount_value
       except Coupon.DoesNotExist:
           messages.error(
               request, "Invalid coupon code. Please enter a valid coupon code."
           )
       for item in cart:
           item.coupon_discount_amount = Coupon_discount

        # Calculate total price for each cart item
       for item in cart:
            item.totalprice = (
                item.product.price * item.product_quantity - item.coupon_discount_amount
            )
            item.save()
            messages.success(
               request, "Coupon Applied Successfully"
             )
   
    # Pass the cart items, total price, and coupon code to the template as context
    context = {
        "cart": cart,
        "total_price": total_price,
        "stock_count_plus_one": stock_count_plus_one,
        "cart_count":cart_count
    }

    # Pass the cart items to the template
    return render(request, "user_side/cart_view.html", context)

    

#_____ Update CArt Quantity________________

@login_required
def update_cart_quantity(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    
    try:
        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
            product_id = request.POST.get("product_id")
            new_quantity = int(request.POST.get("quantity"))
        
            # Retrieve the product object
            product = get_object_or_404(Products, id=product_id)
            

            # Get or create the cart item for the user and product
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=product
            )
          

            # Update the cart item quantity
            cart_item.product_quantity = new_quantity
            cart_item.save()
            
            total_price = product.price * new_quantity
            # Return JSON response with updated details
            return JsonResponse(
                {
                    "success": "Cart quantity updated successfully",

                    'total_price': total_price,
                }
            ) 
        else:
            return JsonResponse({"error": "Invalid request"}, status=400)
    except ValueError:
        return JsonResponse({"error": "Invalid quantity value"}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Internal server error."}, status=500)
    

#__________________-Remove From Cart____________

def remove_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id)
    product = cart_item.product

    # Increase the stock count of the product

    cart_item.delete()
    messages.success(request,"Cart item removed")
    return redirect("user_profile:cart_view")

from django.contrib.auth.hashers import check_password
import re
from django.contrib import messages
from django.shortcuts import redirect

#____________________UPDATE PROFILE________________

def update_profile(request):
    user = request.user
    password = request.POST.get('currentpassword')
    change_user=CustomUser.objects.get(email=user)
    if check_password(password, user.password):
        if user.is_authenticated:
            if request.method == "POST":
                username = request.POST.get('username')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                #Updating Profile
                change_user.username=username
                change_user.first_name=first_name
                change_user.last_name=last_name
                change_user.email=email
                change_user.phone=phone
                change_user.save()
                # Check if the current password is given
              
                messages.success(request, "Profile updated successfully.")
                return redirect('user_profile:user_profile')
            
            else:
                messages.error(request,"Please Login to continue")
    else:
        messages.error(request, "Incorrect Password")
        return redirect('user_profile:user_profile')
    
    
#___________________Reset Password______________

def reset_password(request):
    user=request.user
    password=request.POST.get("currentpassword")
    print(password,"current")
    pass1=request.POST.get("pass1")
    
    if user.is_authenticated:
        if check_password(password, user.password):
            #Change Password
            user.set_password(pass1)
            user.save()
            update_session_auth_hash(request, user)
            # update_session_auth_hash(request, user)
            print(f"User: {user}, Current Password: {user.password}, New Password: {pass1}")
            messages.success(request,"Changed Password Successfully")
            return redirect('home')
        else:
            messages.error(request,"Incorrect Current Password")
            return redirect('user_profile:user_profile')
    else:
        messages.error(request,"Please login to continue")
        return redirect('home')
        

#__________________ORDER CHECKOUT________

def order_checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    # Retrieve saved addresses from the Address model
    user = request.user
    addresses = address.objects.filter(username=user)

    # Retrieve payment modes from the payment module
    payment_modes = dict(payment.PAYMENT_CHOICES)

    # Retrieve cart items from the Cart model for the current user
    cart = Cart.objects.filter(user=user)
    total_amount = 0
    # Calculate the total price for each cart item and print quantity of each product
    for item in cart:
        item.total_price = (
            item.product.price * item.product_quantity
        )
        total_amount += item.total_price
    sub_total=total_amount
    delivery=0
    if total_amount<5000:
        delivery=60
        total_amount+=delivery

    context = {
        "addresses": addresses,
        "cart": cart,
        "payment_modes": payment_modes,
        'sub_total':sub_total,
        "total_amount": total_amount,
        'delivery':delivery
    }

    # Render the checkout template with the context
    return render(request, "user_side/order_checkout.html", context)
                
                
            
#_________________Confirm Orders____________________
@login_required
def confirm_orders(request):
    print("reched here")
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    if request.method == "POST":
        # Process form submission
        user = request.user
        address_id = request.POST.get("saved_address")
        payment_method = request.POST.get("payment_method")
        order_notes=request.POST.get("order_notes")
        cart = Cart.objects.filter(user=user)
        total_price = sum(
            item.product.price * item.product_quantity
            for item in cart
        )

        for item in cart:
            product = item.product
            quantity = item.product_quantity

            product.stock_count -= quantity
            # Update stock count
            product.save()

        if not payment_method:
            payment_method = "unknown"
        # Create the order
        print("here")
        order = Order.objects.create(
            user=user,
            address_id=address_id,
            total_price=total_price,
            payment_method=payment_method,
            order_notes=order_notes,
        )

        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.product_quantity,
                price=item.product.price * item.product_quantity,
            )

        # Clear the cart
        

        messages.success(request, "Order placed successfully.")
        return redirect("user_profile:order_confirmation", order_id=order.id)
    else:
        # Display the checkout page with the form
        user = request.user
        addresses = address.objects.filter(username=user)
        cart_items = Cart.objects.filter(user=user)
        payment_modes = dict(payment.PAYMENT_CHOICES)
        total = sum(item.product.price * item.product_quantity for item in cart_items)

        context = {
            "addresses": addresses,
            "cart_items": cart_items,
            "payment_modes": payment_modes,
            "total": total,
        }
        return render(request, "user_auth/confirm_orders.html", context)

def order_confirmation(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.all()
    cart = Cart.objects.filter(user=request.user)  # Fetch related OrderItem objects
    cart.delete()
    context = {
        "order": order,
        "order_items": order_items,  # Pass the order items to the template
    }
    return render(request, "user_side/order_confirmed.html", context)



# View Function for Cancelling Order
# ---------------------------------------------------------------------------------------------------------------------------
@login_required
def cancel_order(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    order = get_object_or_404(Order, id=order_id)

    if order.status != "Shipped":
        # Cancel the order
        order.status = "Cancelled"
        order.save()

        # Update product stock_count for each OrderItem in the order
        for order_item in order.orderitem_set.all():
            product = order_item.product
            product.stock_count += order_item.quantity
            product.save()

        return redirect("user_profile:user_profile")
    else:
        # Handle error or redirect to appropriate page
        return redirect("some_error_page")
    
#______________Order View_________

def order_view(request,id):
    user=request.user
    if user.is_authenticated:
        order = Order.objects.get(id=id)
        
        context={
            'order' : order
        }
        return render(request,"user_side/order_view.html",context)
    else:
        redirect("login")
        
    

