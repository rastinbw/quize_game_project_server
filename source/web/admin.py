from django.contrib import admin
from .models import Token, Profile, Guest

# Register your models here.
admin.site.register(Token)
admin.site.register(Profile)
admin.site.register(Guest)
