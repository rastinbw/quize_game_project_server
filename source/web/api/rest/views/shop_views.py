import json
from uuid import uuid4
import web.consts as constant
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from web.helpers import RSAEncryption, Generator, JsonResponse
from web.models import Shop, ShopItem

@method_decorator(csrf_exempt, name='dispatch')
class ShopVersion(View):
    def get(self, request):
        shop = Shop.objects.all().get()

        version = shop.version

        shop_version_dict = {
            'version':version
        }

        return JsonResponse(json.JSONEncoder().encode(shop_version_dict))


@method_decorator(csrf_exempt, name='dispatch')
class GetShop(View):
    def get(self, request):
        shop = Shop.objects.all().get()

        version = shop.version
        image = shop.image
        title = shop.title


        shop_items = []

        for item in ShopItem.objects.all():
            shop_items.append(item.item_id)


        shop_dict = {
            'version': version,
            'image':image,
            'title':title,
            'items':shop_items,
        }

        return JsonResponse(json.JSONEncoder().encode(shop_dict))