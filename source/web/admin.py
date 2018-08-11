from django.contrib import admin
from .models import Token, Profile, Guest, Barzakh

# Register your models here.


class BarzakhAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created')


admin.site.register(Barzakh, BarzakhAdmin)
admin.site.register(Token)
admin.site.register(Profile)
admin.site.register(Guest)
