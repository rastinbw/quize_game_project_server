import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'source.settings')

import django
django.setup()


# FAKE POP SCRIPT
import random
from web.models import Guest, Barzakh
from faker import Faker
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

fakegen = Faker()
fields = ['riazi', 'tajrobi', 'ensani']
grades = ['10th', '11th', '12th']


def add_guest():
    # creating fake data for entry
    fake_date = fakegen.date()
    # and many other fake data you can find in documentation

    guest = Guest.objects.get_or_create(created=fake_date,
                                        guest_field=random.choice(fields),
                                        guest_grade=random.choice(grades))[0]
    guest.save()
    return guest


def add_user():
    username = 'user_{}'.format(fakegen.name().replace(" ", ""))
    email = '{}@example.com'.format(username)
    password = get_random_string(50)
    user = User.objects.get_or_create(username=username, email=email, password=password)[0]

    Barzakh.objects.create(user=user,
                           field=random.choice(fields),
                           grade=random.choice(grades))


def populate(n=2):
    for entry in range(n):
        add_user()


if __name__ == '__main__':
    print("populating script!")
    populate()
    print("populating done!")
