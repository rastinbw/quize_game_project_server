from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import time

@method_decorator(csrf_exempt, name='dispatch')
def test(request):
    # data = request.POST.get('data')
    # load_data = json.loads(data)

    # #
    # new_hello = "{} my friend".format(load_data['hello'])
    # #
    # #
    # # test = {
    # #     'hello':new_hello
    # # }
    user = 'ali'

    cache.set( user, {
        'firstname': 'alireza',
        'age': 21,
        'list': [1, 2, 3, 4],
        'tuple': (1, 2, 3, 4),
        'dict': {'A': 1, 'B': 2},
    },timeout = 1)

    print(cache.get(user))
    time.sleep(2)
    print(cache.get(user))

    return HttpResponse("hello")