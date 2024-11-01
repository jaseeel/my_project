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
            if user is not None and not user.is_superuser:
                if not user.is_active:
                    errors['general']= "Your account is blocked. Please contact support for assistance."
                    return render(request, 'registration/login.html', {'errors': errors, 'email': email})

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
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def cancel_view(request):
    # Ensure that 'email' is in the session
    if 'email' in request.session:
        try:
            user = CustomUser.objects.get(email=request.session['email'])
            user.delete()
            messages.info(request, "User account deleted successfully.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
        finally:
            del request.session['email']
            logout(request)
            messages.info(request, "You have been logged out.")
            return redirect('home')
    else:
        messages.error(request, "No user session found.")
        return redirect('login')


#____________Forgot Password__________
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

import re
import random
import string



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        
        # Email validation
        pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern_email, email):
            messages.error(request, "Please enter a valid email")
            return render(request, 'registration/forget.html')
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with this email address")
            return render(request, 'registration/forget.html')
        
        # Send OTP via email
        message = generate_otp()
        sender_email = os.getenv("MY_EMAIL")
        receiver_email = email
        password_email = os.getenv("MY_KEY")
        receiver_email = [email]
        try:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.set_debuglevel(1)
                    server.login(sender_email, password_email)
                    server.sendmail(sender_email, receiver_email, f"Your OTP for sportsio password reset is {message}")
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return render(request, 'registration/forget.html')
        
        # Store OTP and email in session
        request.session['reset_email'] = email
        request.session['reset_otp'] = message
        print(message)
        
        messages.success(request, 'OTP has been sent to your email')
        return redirect('reset_otp')  
    
    return render(request, 'registration/forget.html')

def reset_otp(request):
    if request.method == 'POST':

        stored_otp = request.session.get('reset_otp')
        otp1       =  request.POST['otp1']
        otp2=request.POST['otp2']
        otp3=request.POST['otp3']
        otp4=request.POST['otp4']
        otp5=request.POST['otp5']
        otp6=request.POST['otp6']     
        OTP=(str(otp1)+str(otp2)+str(otp3)+str(otp4)+str(otp5)+str(otp6))
        
        if OTP == stored_otp:
            del request.session['reset_otp']
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'registration/reset_otp.html')

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
       
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/reset_password.html')
       
        # Password validation
        pattern_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if not re.match(pattern_password, new_password):
            messages.error(request, "Password must contain at least 8 characters of capital letter, small letter and symbol")
            return render(request, 'registration/reset_password.html')
       
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, 'Password reset session has expired. Please start over.')
            return redirect('forgot_password')

        try:
            user = CustomUser.objects.get(email=email)
            print(user)
            user.set_password(new_password)
            print(user.password)
            user.save()
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found. Please try the password reset process again.')
            return redirect('forgot_password')
       
        messages.success(request, 'Password changed successfully')
        del request.session['reset_email']
        return redirect('login')
   
    return render(request, 'registration/reset_password.html')