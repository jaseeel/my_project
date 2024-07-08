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
from django import forms
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 


# Create your views here.

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))

def generate_otp(length=6):
    return ''.join(secrets.choice("0123456789") for i in range(length))

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            phone = form.cleaned_data['phone']

            # Regex patterns for validation
            pattern_username = r'^[a-zA-Z0-9]+$'
            pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            pattern_phone = r'^(?!0{10}$)\d{10}$'
            pattern_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

            errors = {}

            if not re.match(pattern_username, username):
                errors['username'] = "Username cannot contain any symbols"

            if not re.match(pattern_email, email):
                errors['email'] = "Please enter a valid email"

            if not re.match(pattern_password, password):
                errors['password'] = "Password must contain at least 8 characters of capital letter, small letter and symbol"

            if not re.match(pattern_phone, phone):
                errors['phone'] = "Please enter a valid phone number"

            if password != password2:
                errors['password2'] = "Passwords do not match"

            if CustomUser.objects.filter(email=email).exists():
                errors['email'] = "Email already exists"

            if CustomUser.objects.filter(username=username).exists():
                errors['username'] = "Username already exists"

            if CustomUser.objects.filter(phone=phone).exists():
                errors['phone'] = "Phone number already exists"

            if errors:
                for field, error in errors.items():
                    form.add_error(field, error)
                return render(request, 'registration/register.html', {'form': form})

            message = generate_otp()
            sender_email = os.getenv("MY_EMAIL")
            receiver_email = email
            password_email = os.getenv("MY_KEY")

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.set_debuglevel(1)
                    server.login(sender_email, password_email)
                    server.sendmail(sender_email, receiver_email, f"Your OTP for sportsio is {message}")
            except smtplib.SMTPAuthenticationError:
                messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
                return redirect('register')

            user = CustomUser.objects.create_user(
                email=email, password=password, phone=phone,
                username=username, first_name=first_name, last_name=last_name
            )
            user.save()

            request.session['email'] = email
            request.session['otp'] = message
            print(message)
            messages.success(request, 'OTP is sent to your email')
            return redirect('otp')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        errors = {}

        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'

        if not password:
            errors['password'] = 'Password is required.'

        if not errors:
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_active and not user.is_superuser:
                login(request, user)
                messages.success(request, "You have logged in successfully")
                return redirect('home')
            else:
                errors['general'] = 'Invalid email or password.'

        return render(request, 'registration/login.html', {'errors': errors, 'email': email})
    
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