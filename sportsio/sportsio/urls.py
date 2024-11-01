"""
URL configuration for sportsio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from user_side import views
from userprofile import views as prof
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.conf.urls import handler404


def custom_404(request, exception):
    
    return render(request, '404.html', status=404)
handler404 = custom_404

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/',include('admin_side.urls')),
    path('',views.home, name='home'),
    path('base', views.base, name='base'),
    path('register/', include('registration.urls')),
    path('user_side/', include(('user_side.urls', 'user_side'), namespace='user_side')),
    path('user_profile/', include(('userprofile.urls', 'user_profile'), namespace='user_profile')),
    path('auth/', include('social_django.urls', namespace='social')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
