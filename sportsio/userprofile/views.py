from django.shortcuts import render, get_object_or_404

from inventory.models import Coupon,Transaction
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
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Max
from django.views.decorators.csrf import ensure_csrf_cookie
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.utils.timezone import now as timezone_now

# Create your views here.

#_____________Account Page ________________

def user_profile(request):
    user=request.user
    if user.is_authenticated:
        addresses=address.objects.filter(username=user)
        reset_user=CustomUser.objects.filter(username=user)
        cart_count=Cart.objects.filter(user=request.user).count()
        wallet_balance=request.user.wallet_balance
        wallet_history = Transaction.objects.filter(user=request.user).order_by('-timestamp')
        
 
 
        # Fetch orders related to the current user
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

        context={
             'user':user,
             'address':addresses,
             "reset_user":reset_user,
             "orders": user_orders,
             'cart_count':cart_count,
             "wallet_balance":wallet_balance,
             "wallet_history":wallet_history,
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
        if request.GET.get('redirect')=="checkout":
            return redirect("user_profile:order_checkout")
        else:
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
    if request.user.is_authenticated:
        if request.method == 'POST':
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
                        return JsonResponse({'status': "No stocks left"})
            else:
                return JsonResponse({'status': "Product not found"})
    else:
        # Use Django's messaging framework to inform the user
        return JsonResponse({'status': "Login Required"})
    


# ______________Cart_view_________
def cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")

    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.offer_price * item.product_quantity for item in cart_items)
    sub_total = sum(item.product.price * item.product_quantity for item in cart_items)
    saved_price= sub_total-total_price
    
    # To set maximum quantity can be added to cart
    max_stock_count_plus_one = Products.objects.aggregate(Max("stock_count"))["stock_count__max"] or 1
    stock_count_plus_one = max_stock_count_plus_one


    context = {
        "cart": cart_items,
        "sub_total": float(sub_total),  # Same consideration as above
        "total_price": float(total_price),  # Same consideration as above
        "stock_count_plus_one": stock_count_plus_one,
        'saved_price':saved_price,
    }

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
            cart_items = Cart.objects.filter(user=request.user)
            

            # Get or create the cart item for the user and product
            cart_item, created = Cart.objects.get_or_create(
                user=request.user, product=product
            )
          

            # Update the cart item quantity
            cart_item.product_quantity = new_quantity
            cart_item.save()

        
            total_price = sum(item.product.offer_price * item.product_quantity for item in cart_items)
            sub_total = sum(item.product.price * item.product_quantity for item in cart_items)
            saved_price= sub_total-total_price
            # Return JSON response with updated details
            return JsonResponse(
                {
                    "success": "Cart quantity updated successfully",

                    'total_price': total_price,
                    'sub_total':sub_total,
                    'saved_price':saved_price
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
@csrf_exempt
def order_checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    # Retrieve saved addresses from the Address model
    user = request.user
    coupon_message=""
    total_amount = 0
    addresses = address.objects.filter(username=user)

    # Retrieve payment modes from the payment module
    payment_modes = dict(payment.PAYMENT_CHOICES)
    wallet_balance=user.wallet_balance
    # Retrieve cart items from the Cart model for the current user
    cart = Cart.objects.filter(user=user)
    Coupon_discount=0
    # Calculate the total price for each cart item and print quantity of each product
    total_amount = sum(item.product.offer_price * item.product_quantity for item in cart)
    sub_total=total_amount
    for item in cart:
        item.total_price = (
            item.product.offer_price * item.product_quantity
        )
        item.save()
    #Apply Coupon Here
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.expiration_date < timezone_now().date() :
                messages.error(request,"Coupon Expired")
            elif total_amount < coupon.min_order_value:
                messages.error(request,"Total Price Sould Be More Than {}".format(coupon.min_order_value))
                coupon_message="Total Price Sould Be More Than {}".format(coupon.min_order_value)
            else:
                if coupon.discount_type == "percentage":
                    Coupon_discount = (total_amount * coupon.discount_value) / 100
                elif coupon.discount_type == "fixed":
                    Coupon_discount = coupon.discount_value
                # Apply Coupon Discount to the price

                total_amount -= Coupon_discount
                
                print(Coupon_discount)
                messages.success(request, "Coupon Applied Successfully")
                coupon_message="'{}' Applied successfully".format(coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code. Please enter a valid coupon code.")

    if 'delivery' in request.session:
        del request.session['delivery']
    delivery=0
    if total_amount<5000:
        delivery=60
        total_amount+=delivery
    request.session['delivery']=delivery
    
    context = {
        "addresses": addresses,
        "cart": cart,
        "payment_modes": payment_modes,
        'sub_total':total_amount,
        "total_amount": sub_total,
        'delivery':delivery,
        'Coupon_discount':Coupon_discount,
        'coupon_message':coupon_message,
        "wallet_balance":wallet_balance,
    }

    # Render the checkout template with the context
    return render(request, "user_side/order_checkout.html", context)
                
                
            
#_________________Confirm Orders____________________
@login_required
def confirm_orders(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    if request.method == "POST":
        # Process form submission
        user = request.user
        
        address_id = request.POST.get("saved_address")
        payment_method = request.POST.get("payment_method")
        order_notes=request.POST.get("order_notes")
        coupon_used=request.POST.get("code")
        discount_price=request.POST.get("discount_price")
        total_price=request.POST.get('total_price')
        cart = Cart.objects.filter(user=user)

        
        

        for item in cart:
            product = item.product
            quantity = item.product_quantity

            product.stock_count -= quantity
            # Update stock count
            product.save()

        if not payment_method:
            payment_method = "unknown"
        # Create the order
        
        order = Order.objects.create(
            user=user,
            address_id=address_id,
            payment_method=payment_method,
            coupon_used=coupon_used,
            order_notes=order_notes,
            total_price=total_price,
            discount_price=discount_price
        )
        #Create Order Items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.product_quantity,
                price=item.product.offer_price * item.product_quantity,
            )
        cart = Cart.objects.filter(user=request.user)  # Fetch related OrderItem objects
        cart.delete()
        if payment_method == "walletbalance":
            # Redirect to wallet_payment with order_id
            return redirect("user_profile:wallet_payment", order_id=order.id)
        

        messages.success(request, "Order placed successfully.")
        return redirect("user_profile:order_confirmation", order_id=order.id)
    else:
        # Display the checkout page with the form
        user = request.user
        addresses = address.objects.filter(username=user)
        cart_items = Cart.objects.filter(user=user)
        payment_modes = dict(payment.PAYMENT_CHOICES)
        total = sum(item.product.offer_price * item.product_quantity for item in cart_items)

        context = {
            "addresses": addresses,
            "cart_items": cart_items,
            "payment_modes": payment_modes,
            "total": total,
        }
        return render(request, "user_side/confirm_orders.html", context)
    
    
#_______Wallet Payment________
@login_required
def wallet_payment(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.orderitem_set.all()
    user_profile = request.user


    wallet_balance = user_profile.wallet_balance
    total_price = order.total_price



    if wallet_balance >= total_price > 0:
        print("payment done")
        with transaction.atomic():
            user_profile.wallet_balance -= total_price
            user_profile.save()
            order.paid = True
            order.save()
            Transaction.objects.create(
                 user=order.user,
                 transaction_type='P',
                 amount=total_price
             )
            Cart.objects.filter(user=request.user).delete()
            messages.success(request, "Payment successful. Order placed.")
            return redirect("user_profile:order_confirmation", order_id=order.id)

    context = {
        "order": order,
        "order_items": order_items,
        "wallet_balance": user_profile.wallet_balance,
    }
    return HttpResponse("wallet paid")
    # return render(request, "user_auth/wallet_payment.html", context)

def order_confirmation(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to access wallet payment.")
        return redirect("login")
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.all()
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
        tracking_steps = [
        {"icon": "fa fa-check", "text": "Order confirmed", "active": False},
        {"icon": "fa fa-user", "text": "Picked by courier", "active": False},
        {"icon": "fa fa-truck", "text": "Out_of_delivery", "active": False},
        {"icon": "fa fa-home", "text": "Delivered","active": False},
        {"icon": "fa fa-retweet", "text": "Return","active": False},
        {"icon": "fa fa-credit-card", "text": "Refunded","active": False},
        ]

        if order.status == "Pending":
            tracking_steps[0]["active"] = True
        elif order.status == "Processing":
            tracking_steps[0]["active"] = True
        elif order.status == "Shipped":
            tracking_steps[0]["active"] = True
            tracking_steps[1]["active"] = True
        elif order.status == "Out of delivery" :
            tracking_steps[0]["active"] = True
            tracking_steps[1]["active"] = True
            tracking_steps[2]["active"] = True
        elif order.status == "Delivered" :
            tracking_steps[0]["active"] = True
            tracking_steps[1]["active"] = True
            tracking_steps[2]["active"] = True
            tracking_steps[3]["active"] = True
        elif order.status == "Return" :
            tracking_steps[0]["active"] = True
            tracking_steps[1]["active"] = True
            tracking_steps[2]["active"] = True
            tracking_steps[3]["active"] = True
            tracking_steps[4]["active"] = True
        elif order.status == "Refunded" :
            tracking_steps[0]["active"] = True
            tracking_steps[1]["active"] = True
            tracking_steps[2]["active"] = True
            tracking_steps[3]["active"] = True
            tracking_steps[4]["active"] = True
            tracking_steps[5]["active"] = True

        context = {"order": order, "tracking_steps": tracking_steps}
        

        return render(request,"user_side/order_view.html",context)
    else:
        redirect("login")
        
#_______________Wishlist__________

@login_required
def wishlist(request):
    if request.user.is_authenticated:
        try:
            product_id = int(request.POST.get('product_id'))
            product = get_object_or_404(Products, id=product_id)
        except (ValueError, Products.DoesNotExist):
            messages.error(request, "Invalid product ID or product does not exist.")
            return redirect("home")

        if Wishlist.objects.filter(user=request.user, product=product).exists():
            return JsonResponse({'status': "Product already exists"})
        else:
            wishlist_item = Wishlist(user=request.user, product=product)
            wishlist_item.save()

        return JsonResponse({'status': "Product added to Wishlist"})
    
    return JsonResponse({'status': "Login Required"})



        
#___________---Wish List View---____________
def wishlist_view(request):
    user=request.user
    if user.is_authenticated:
        wishlist_view=Wishlist.objects.filter(user=user)   
        context={
            'wishlist':wishlist_view
        }
        return render(request,"user_side/wishlist.html",context)
    else:
        messages.error(request,"Login to access wishlist")
    return redirect("home")

#_______________--- Delete Wishlist Items---__________
def delete_wishlist(request,id):
    if request.user.is_authenticated:
        w_item=Wishlist.objects.get(user=request.user,id=id)
        w_item.delete()
        messages.success(request,"Removed item")
        return redirect("user_profile:wishlist_view")
    else:
        messages.info("Login to access wishlist")
        return redirect("home")


# ------------------------razorpay----------------------

@csrf_exempt

def razorpay_callback(request):
    if request.method == "POST":
        data = request.POST
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(cart_item.product.offer_price for cart_item in cart_items)
        if 'delivery' in request.session:
            delivery=request.session['delivery']
            total_price+=delivery
        print(delivery)
            
            
        
        
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    total_price=total_price,
                    payment_method="Razorpay",
                    paid=True,  # Assume payment is successful initially
                    razorpay_order_id=data.get("razorpay_payment_id"),
                )
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.product_quantity,
                        price=cart_item.product.price,
                    )
                
                for item in cart_items:
                    product = item.product
                    quantity = item.product_quantity
                    product.stock_count -= quantity
                    product.save()
                
                cart_items.delete()
                
                # Redirect to success page after bn successful payment
                return render(request,
                "user_side/success.html",)
        except Exception as e:
            # If an exception occurs, rollback changes and return error response
            if order:
                order.paid = False
                order.status = "Payment pending"
                order.save()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Only POST method is allowed"}, status=405)



def returnorder(request,id):
    order = get_object_or_404(Order, id=id)
    order.status="Return"
    order.save()
    return redirect("user_profile:user_profile")
    
#Download Invoice _______________

    
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    
    template_path = "user_side/pdf.html"
    context = {"order": order}
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="report.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")

    return response