from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models
from web.helpers import Generator
from django.conf import settings
from django.db.models import Q
from datetime import *

"""
class Purge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    field = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=128, blank=True, default='')
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
"""
#TODO what should u do in purge
class PurgeManager(models.Manager):
    pass

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "{0}: {1}".format(self.created, self.user.username)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    cityId = models.PositiveIntegerField(null=True)
    field = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=128, blank=True, default='')
    phoneNumber = models.CharField(max_length=128, blank=True, default='')
    experience = models.FloatField(default=0)
    level = models.IntegerField(default=0)
    consumable = models.PositiveIntegerField(default=0)
    guest = models.BooleanField(default=True)

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

"""
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
"""

class Contestant(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    state = models.CharField(max_length=128, blank=True, default='')
    contest_id = models.CharField(max_length=128, blank=True, default='')
    join_flag = models.BooleanField()

    def __str__(self):
        return "{0}:{1}".format(self.profile.user.username, self.contest_id)

class Contest(models.Model):
    # TODO do the related__name stuff
    first_user = models.ForeignKey(Contestant, on_delete=models.CASCADE(), related_name='')
    second_user = models.ForeignKey(Contestant, on_delete=models.CASCADE(), related_name='', default=None)
    field = models.CharField(max_length=128, blank=True, default=first_user.profile.field)
    grade = models.CharField(max_length=128, blank=True, default=first_user.profile.grade)
    level = models.IntegerField(default=first_user.profile.level)
    xp = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = PurgeManager()