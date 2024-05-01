from django.shortcuts import render
from .models import *
from admin_side.views import *
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
        return redirect("user_profile")
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
        return redirect('user_profile')
    return render(request,"user_side/edit_address.html",context)
        
