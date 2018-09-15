from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models
from web.helpers import Generator
from django.db.models import Q
from django.conf import settings
from django.utils import timezone


class Purge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    field = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=128, blank=True, default='')
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)


# TODO what should u do in purge
# this manager is for handling the waiting contests

class PurgeManager(models.Manager):
    def search_opponent(self, username):
        # second_user = user.username
        the_user = Profile.objects.filter(user__username=username).get()

        qlookup_is_second_empty = Q(second_user=None)
        qlookup_field = Q(first_user__profile__field=the_user.field)
        qlookup_grade = Q(first_user__profile__grade=the_user.grade)
        qlookup_level = Q(first_user__profile__level__range=(the_user.level-5,the_user.level+5))
        qlookup_except_me = ~Q(first_user__profile__user__username=the_user.user.username)

        available_matches = self.get_queryset().filter(qlookup_is_second_empty & qlookup_field & qlookup_grade & qlookup_except_me & qlookup_level)

        if available_matches.exists():
            print(available_matches)
            return available_matches[0]
        else:
            print("no opponent found!")
            return -1

        # second_user = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='second_user', default=None,
        #                                 blank=True, null=True)

    # class Meta:
    #     ordering = ('created',)
    #
    # def __str__(self):
    #     return "{0}: {1}".format(self.created, self.user.username)


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

    # TODO is_ban(bool) and ban_date (dateField)

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


class Contestant(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    state = models.CharField(max_length=128, blank=True, default='')
    contest_id = models.CharField(max_length=128, blank=True, default='')
    join_flag = models.BooleanField()

    def __str__(self):
        return "{0}".format(self.profile.user.username)


class Contest(models.Model):
    # TODO do the related__name stuff
    first_user = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='first_user')
    second_user = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='second_user', default=None, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    CID = models.CharField(max_length=167, )
    # field = models.CharField(max_length=128, blank=True, default='')
    # grade = models.CharField(max_length=128, blank=True, default='')
    # level = models.IntegerField(default=0)
    # # xp = models.IntegerField(default=0)
    #
    # def save(self, *args, **kwargs):
    #     self.field = self.first_user.profile.field
    #     self.grade = self.first_user.profile.grade
    #     self.level = self.first_user.profile.level
    #
    #     super(Contest, self).save(*args, **kwargs)

    objects = PurgeManager()

    def __str__(self):
        return "{0} vs {1}".format(self.first_user, self.second_user)