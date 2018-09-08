from django.contrib import admin
from .models import Token, Profile, Contestant, Contest

# Register your models here.


class BarzakhAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created')

#admin.site.register(Purge, BarzakhAdmin)
admin.site.register(Token)
admin.site.register(Profile)
admin.site.register(Contestant)
admin.site.register(Contest)
# admin.site.register(Guest)
