from rest_framework import views
from rest_framework.response import Response
from django.contrib.auth.models import User
from web.models import Token, Profile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


class Register(views.APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({'Error': "Please provide data"}, status="400")

        data = request.data.get('data')
        # TODO decrypt data first

        # deserialize data
        try:
            obj = json.loads(data)
        except ValueError:
            return Response({'Error': "Invalid json format"}, status="400")

        username = obj.get('username')
        email = obj.get('email', '')
        password = obj.get('password')

        city_id = obj.get('city_id')
        school_id = obj.get('school_id')
        phone_number = obj.get('phone_number', '')

        if not User.objects.filter(username=username).exists():
            if email == '' or not User.objects.filter(email=email).exists():
                user = User.objects.create(
                    username=username,
                    password=password,
                    email=email,
                )
                user.save()

                profile = Profile.objects.create(
                    user=user,
                    cityId=city_id,
                    schoolId=school_id,
                    phoneNumber=phone_number,
                )
                profile.save()

                token = Token.objects.create(user=user)
                token.save()
            else:
                return Response({'Error': "Email Exists in database"}, status="400")
        else:
            return Response({'Error': "Username Exists in database"}, status="400")

        return Response(
            {'token': token.token},
            status=200,
            content_type="application/json"
        )


class Login(views.APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({'Error': "Please provide username/password"}, status="400")

        data = request.data.get('data')
        # TODO decrypt data first

        try:
            obj = json.loads(data)
        except ValueError:
            return Response({'Error': "Invalid json format"}, status="400")

        username = obj.get('username')
        password = obj.get('password')

        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            return Response({'Error': "Invalid username/password"}, status="400")
        if user:
            token = {'token': user.token.token}

            return Response(
                token,
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                {'Error': "Invalid credentials"},
                status=400,
                content_type="application/json"
            )


@csrf_exempt
def save(request):
    data = request.POST.get('content')
    if data:
        username = data
        password = 5555555

        user = User.objects.create(username=username, password=password)
        user.save()

        return HttpResponse('OK')
