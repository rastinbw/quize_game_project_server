import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'first_project.settings')

import django
django.setup()


# FAKE POP SCRIPT
import random
from web.models import Guest
from faker import Faker


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


def populate(n=5):
    for entry in range(n):
        add_guest()


if __name__ == '__main__':
    print("populating script!")
    populate(10)
    print("populating done!")
