from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
from django.db.models.signals import post_save
from django.dispatch import receiver


def generate_unique_token(token_field="token",
                          token_function=lambda: uuid4().hex):
    """
    Generates random tokens until a unique one is found
    :param Model: a Model class that should be searched
    :param token_field: a string with the name of the token field to search in the model_class
    :param token_function: a callable that returns a candidate value
    :return: the unique candidate token
    """
    unique_token_found = False
    while not unique_token_found:
        token = token_function()
        # This weird looking construction is a way to pass a value to a field with a dynamic name
        if Token.objects.filter(**{token_field: token}).count() is 0:
            unique_token_found = True
    return token


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    cityId = models.PositiveIntegerField()
    schoolId = models.PositiveIntegerField()
    phoneNumber = models.CharField(max_length=128, blank=True, default='')

    class Meta:
        ordering = ('created',)

    # @receiver(post_save, sender=User)
    # def create_user_profile(self, instance, created, **kwargs):
    #     if created:
    #         Profile.objects.create(user=instance)
    #
    # @receiver(post_save, sender=User)
    # def save_user_profile(self, instance, **kwargs):
    #     instance.profile.save()

    def __str__(self):
        return "{0}:{1}".format(self.created, self.user.username)


class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.token = generate_unique_token()
        super(Token, self).save(*args, **kwargs)

    def __str__(self):
        return "{}: token_{}".format(self.user, self.token)

