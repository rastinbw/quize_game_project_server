from web.models import Barzakh
from celery import task
from datetime import timedelta
from django.utils import timezone

barzakh_limit_time = 3  # minutes


@task
def check_barzakh():
    for item in Barzakh.objects.all():
        min_diff = get_difference_from_now(item.created)
        if min_diff >= barzakh_limit_time:
            # todo pair the item.user with a bot to play with
            item.delete()

    # todo remove this line later
    return [get_difference_from_now(item.created) for item in Barzakh.objects.all()]


def get_difference_from_now(time):
    now = timezone.now()
    return (now - time) // timedelta(minutes=1)
