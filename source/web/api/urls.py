"""source URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from django.urls import path

from web.api.views import registration_views

urlpatterns = [
    path('user/login/', registration_views.Login.as_view(), name='user-login'),
    path('user/register/', registration_views.Register.as_view(), name='user-register'),
    path('guest/register/', registration_views.GuestRegister.as_view(), name='guest-register'),


    path('generate/', registration_views.generate_private_key),
    path('test/', registration_views.Test.as_view())
]

