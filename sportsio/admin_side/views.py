from django.contrib import messages
from django.shortcuts import redirect, render
from admin_side.models import *
from django.contrib.auth import login,logout

#------------------------------------------------------------Admin Login
 
def admin_login(request):
    if 'email' in request.session:
        return redirect('dashboard')
    else:
        if request.method=='POST':
            email=request.POST.get('email')
            password=request.POST.get('password')

            if CustomUser.objects.filter(email=email).exists():
                user_obj=CustomUser.objects.get(email=email,is_superuser=True)
                if user_obj.check_password(password):
                    request.session['email']=email
                    login(request,user_obj)
                    return redirect('dashboard')
                else:
                    messages.error("wrong credentials")
            else:
                messages.error("User not Found")   

        return render(request,'admin_side/admin_login.html')

#-------------------------------------------------------------Dashboard view
def dashboard(request):
    return render(request,'admin_side/index.html')      

#-------------------------------------------------------------User management

def User_management(request):
    if 'email' in request.session:

        user = CustomUser.objects.filter(is_superuser=False)
        context={
            'user':user,
        } 
        return render(request,'admin_side/user_management.html',context )
    else: 
            return redirect('admin_login')
    


# -----------------------------------------Block-user

def block(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    user.is_active=False
    user.save()
    return redirect('user_management')

#-------------------------------------------Unblock-user

def unblock(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    user.is_active=True
    user.save()
    return redirect('user_management')

#---------------------------------Delete User

def delete_user(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    user.delete()
    return redirect('user_management')

#-----------------------------------User View

def userviewdetails(request,user_id):
    if 'email' in request.session:
        user=CustomUser.objects.get(id=user_id)
        context={
        'user':user,
        }
        return render(request, 'admin_side/userviewdetails.html',context)
    
#----------------------------------------Admin logout    

def admin_logout(request):
    if 'email' in request.session:
        logout(request)
        request.session.flush()
    return redirect('admin_login')
    
    
    

