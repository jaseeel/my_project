import secrets
import smtplib
from django.contrib import messages
import re
from django.shortcuts import redirect, render
from admin_side.models import CustomUserManager,CustomUser
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 


# Create your views here.
def register(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        phone=request.POST.get('phone')
        
        print(username, email, phone, email)
        
        # Regex patterns for validation
        # pattern_username = r'^[a-zA-Z0-9].*'
        pattern_username = r'^[a-zA-Z0-9]+$'
        pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        pattern_phone = r'^(?!0{10}$)\d{10}$'
        pattern_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        
        if not all([first_name,last_name, username, password, password2, email, phone]):
            messages.error(request, "Please fill all required fields")
            return render(request, 'registration/register.html')

        elif not re.match(pattern_username, username):
            messages.error(request, "Username cannot contain any symbols")
            return render(request, 'registration/register.html')

        elif not re.match(pattern_email, email):
            messages.error(request, "Please enter a valid email")
            return render(request, 'registration/register.html')

        elif not re.match(pattern_password, password):
            messages.error(request, "Password must contain atleast 8 characters of capital letter,small letter and symbol ")
            return render(request, 'registration/register.html')

        elif not re.match(pattern_phone, phone):
            messages.error(request, "Please enter a valid phone number")
            return render(request, 'registration/register.html')

        elif password != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'registration/register.html')
        
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'registration/register.html')
        
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request,"Username already exists")
            return render(request, "registration/register.html")
        elif CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists")
            return render(request, 'registration/register.html')
        
        
        else:
            message= generate_otp()
            sender_email=os.getenv("MY_EMAIL")
            receiver_email=email
            password_email=os.getenv("MY_KEY")
    
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.set_debuglevel(1)
                server.login(sender_email, password_email)
                server.sendmail(sender_email, receiver_email, "Your otp for sportsio is {}".format(message))
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return redirect('register')
    
        user=CustomUser.objects.create_user(email=email, password=password, phone=phone, username=username, first_name=first_name, last_name=last_name)
  
        user.save()
        
        request.session['email'] =  email
        request.session['otp']   =  message
        print(message)       
        messages.success(request,'OTP is sent to your email')
        return redirect('otp')
        

    return render(request, 'registration/register.html')


def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length))


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            user = authenticate(request, email=email, password=password)
            
            if user is not None and user.check_password(password):
                if not user.is_superuser and user.is_active:
                    login(request, user)
                    messages.success(request,"You have logged in successfully")
                    return redirect('home')
            else:
                # Authentication failed
                messages.error(request, "Invalid email or password")
                return render(request, 'registration/login.html', {'invalid_credentials': True})
    
    return render(request, 'registration/login.html')



def forget(request):
    return render(request,'registration/forget.html')


def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length))



@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def verify_otp(request):
    context = {
        'messages': messages.get_messages(request)
    }
    
    
    if request.method == "POST":
        user      = CustomUser.objects.get(email=request.session['email'])
        x         =  request.session.get('otp')
       
        otp1       =  request.POST['otp1']
        otp2=request.POST['otp2']
        otp3=request.POST['otp3']
        otp4=request.POST['otp4']
        otp5=request.POST['otp5']
        otp6=request.POST['otp6']     
        OTP=(str(otp1)+str(otp2)+str(otp3)+str(otp4)+str(otp5)+str(otp6))
        
        if OTP == x:
            
            del request.session['email'] 
            del request.session['otp']       
            messages.success(request, "Signup successful!")
            return redirect('home')
        else:
            user.delete()
            messages.info(request,"invalid otp")
            del request.session['email']
            return redirect('register')
    return render(request,'registration/verify.html',context)

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def cancel_view(request):
    
    user      = CustomUser.objects.get(email=request.session['email'])
    user.delete()
    messages.info(request,"invalid otp")
    del request.session['email']
    return redirect('login')