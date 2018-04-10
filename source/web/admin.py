from django.contrib import admin
from django.contrib.auth.models import User
from .models import Token, Profile

# Register your models here.
admin.site.register(Token)
admin.site.register(Profile)
