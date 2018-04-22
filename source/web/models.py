from django.db import models
from django.contrib.auth.models import User
from web.helpers import Generator
from uuid import uuid4


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    cityId = models.PositiveIntegerField(null=True)
    field = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=128, blank=True, default='')
    phoneNumber = models.CharField(max_length=128, blank=True, default='')

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "{0}:{1}".format(self.created, self.user.username)


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.token = Generator.generate_uuid(Token, 'token')
        super(Token, self).save(*args, **kwargs)

    def __str__(self):
        return "{}: token_{}".format(self.user, self.token)


class Guest(models.Model):
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    guest_id = models.CharField(max_length=128, blank=True, default='')
    guest_field = models.CharField(max_length=128, blank=True, default='')
    guest_grade = models.CharField(max_length=128, blank=True, default='')

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        self.guest_id = Generator.generate_uuid(Guest,
                                                'guest_id',
                                                'Guest',
                                                lambda: uuid4().hex[:9])
        super(Guest, self).save(*args, **kwargs)

    def __str__(self):
        return "{0}:{1}".format(self.created, self.guest_id)




