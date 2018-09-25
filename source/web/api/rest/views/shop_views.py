import json
from uuid import uuid4

import datetime

from django.db.models.fields.files import ImageFieldFile

import web.consts as constant
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from web.helpers import RSAEncryption, Generator, JsonResponse
from web.models import Shop, ShopItem

from django.core import serializers

@method_decorator(csrf_exempt, name='dispatch')
class ShopVersion(View):
    def get(self, request):
        shop = Shop.objects.all().get()

        version = shop.version

        shop_version_dict = {
            'version':version
        }

        return JsonResponse(
            Generator.generate_result(message=shop_version_dict),
        )
        # return JsonResponse(json.JSONEncoder().encode(shop_version_dict))


@method_decorator(csrf_exempt, name='dispatch')
class GetShop(View):
    def get(self, request):
        shop = Shop.objects.all().get()

        version = shop.version
        image = str(shop.image)
        title = shop.title

        shop = ShopItem.objects.all()

        shop_items = []


        for record in shop:
            item = dict(item_id=record.item_id, title=record.title, info=record.info, image=str(record.image),
                        price=record.price, lastprice=record.last_price)
            shop_items.append(item)

        shop_dict = {
            'version': version,
            'image':image,
            'title':title,
            'items':shop_items,
        }

        return JsonResponse(
            Generator.generate_result(message=shop_dict),
        )

