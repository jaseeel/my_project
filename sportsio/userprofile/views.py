from django.shortcuts import render
from .models import *
from admin_side.views import *
# Create your views here.

#_____________Account Page ________________

def user_profile(request):
    user=request.user
    # if not user.is_authenticated:
    #     redirect('login')
    # if user.is_authenticated:
    # address=address.objects.filter(username=user)
    # 'address':address
    context={
         'user':user
         
     }
    return render(request,"user_side/user_profile.html",context)
#  else:
#      return render('user_side/main.html')

def add_address(request):
    user = request.user
    addresses = address.objects.filter(username=user)

    if request.method == "POST":
        house_name = request.POST.get("house_name")
        street = request.POST.get("street")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip")

        # Create a new Address object associated with the current user
        address.objects.create(
            username=user,
            house_name=house_name,
            street=street,
            city=city,
            state=state,
            zipcode=zip_code,
        )

        # Update the addresses queryset to include the new address
        return redirect("user_profile")
    return render(request, "user_side/add_address.html")

    
        
    





#__________________ Manage Address  __________________

def manage_address(request):
    user = request.user
    addresses = address.objects.filter(username=user)

    if request.method == "POST":
        house_name = request.POST.get("house_name")
        street = request.POST.get("street")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip")

        # Create a new Address object associated with the current user
        address.objects.create(
            username=user,
            house_name=house_name,
            street=street,
            city=city,
            state=state,
            zipcode=zip_code,
        )

        # Update the addresses queryset to include the new address
        return redirect("user_profile:manage_address")

    context = {
        "Address": addresses,
    }
    return render(request, "user_auth/manage_address.html", context)

