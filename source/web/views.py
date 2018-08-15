from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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

    return HttpResponse("hello")