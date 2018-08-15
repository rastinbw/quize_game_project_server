from django.contrib import admin
from .models import Token, Profile, Guest, Purge

# Register your models here.


class BarzakhAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created')


admin.site.register(Purge, BarzakhAdmin)
admin.site.register(Token)
admin.site.register(Profile)
admin.site.register(Guest)
