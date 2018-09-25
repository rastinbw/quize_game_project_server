import json
from uuid import uuid4

import web.consts as constant
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from web.helpers import RSAEncryption, Generator, JsonResponse
from web.models import Token, Profile, City


@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request, *args, **kwargs):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('is_encrypted'):
            obj = Generator.generate_dict_from_enc(deserialized_data.get('message'),
                                                   deserialized_data.get('key'))
        else:
            obj = deserialized_data.get('message')

        # Navigating through 'user info' in message part of data and save it into database
        str_token = obj.get('token')
        username = obj.get('username')
        email = obj.get('email', '')
        password = obj.get('password')

        city_id = obj.get('city_id')
        phone_number = obj.get('phone_number', '')

        # Check whether input username is already in database or not
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                Generator.generate_result(result_code=constant.repetitive_username),
            )

        # Check whether input email is already in database or not
        if email != '' and User.objects.filter(email=email).exists():
            return JsonResponse(
                Generator.generate_result(result_code=constant.repetitive_email),
            )

        # Check whether input phone number is already in database or not
        if phone_number != '' and Profile.objects.filter(phoneNumber=phone_number).exists():
            return JsonResponse(
                Generator.generate_result(result_code=constant.repetitive_phone_number)
            )


        # the guests registering
        if Token.objects.filter(token=str_token).exists():
            token = Token.objects.filter(token=str_token).get()

            guest_user = token.user

            guest_user.username = username
            guest_user.password = password
            guest_user.email = email
            guest_user.save()

            Profile.objects.filter(user=guest_user).update(
                user=guest_user,
                cityId=city_id,
                phoneNumber=phone_number,
                guest=False,
            )

            return JsonResponse(
                Generator.generate_result(result_code=constant.success),
            )
        else:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_token),
            )


        # saving user in database
        # user = User.objects.create(
        # 	username=username,
        # 	password=password,
        # 	email=email,
        # )
        # user.save()
        # # making a profile for previous user
        # profile = Profile.objects.create(
        # 	user=user,
        # 	cityId=city_id,
        # 	phoneNumber=phone_number,
        # 	guest=False,
        # )
        # profile.save()
        #
        # # creating a token for previous user
        # token = Token.objects.create(user=user)
        # token.save()

        # preparing and sending result to client
        # message = {'token': token.token, }

        # it checks if the user is guest


        # # create new token for new user
        # elif not Token.objects.filter(token=token).exists():
        # 	token = Token.objects.create(user=user)
        # 	token.save()
        # else:
        # 	return JsonResponse(
        # 		Generator.generate_result(result_code=constant.invalid_token)
        # 	)




@method_decorator(csrf_exempt, name='dispatch')
class Login(View):
    def post(self, request, *args, **kwargs):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('is_encrypted'):
            obj = Generator.generate_dict_from_enc(deserialized_data.get('message'),
                                                   deserialized_data.get('key'))
        else:
            obj = deserialized_data.get('message')

        # Navigating through 'user info' in message part of data and try to authorize it
        username = obj.get('username', '')
        email = obj.get('email', '')
        password = obj.get('password')

        # Check whether user provided username or email
        if username == '' and email == '':
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_username_or_email),
            )

        # Check whether user with input username/password exists in database
        if username != '':
            try:
                user = User.objects.get(username=username, password=password)
            except User.DoesNotExist:
                return JsonResponse(
                    Generator.generate_result(result_code=constant.wrong_username_and_password),
                )

        # Check whether user with input email/password exists in database
        else:
            try:
                user = User.objects.get(email=email, password=password)
            except User.DoesNotExist:
                return JsonResponse(
                    Generator.generate_result(result_code=constant.wrong_email_and_password),
                )

        # preparing and sending result to client
        # TODO this message must be encrypted
        message = {'token': user.token.token, }

        return JsonResponse(
            Generator.generate_result(message=message, key=deserialized_data.get('key')),
        )


@method_decorator(csrf_exempt, name='dispatch')
class GuestRegister(View):
    def get(self, request):

        """
        this view creates a guest and
        returns the generated guest uuid for
        authentication to client
        """

        guest = User.objects.create(
            username=Generator.generate_uuid(User,
                                             'username',
                                             'User',
                                             lambda: uuid4().hex[:9]),
        )
        guest.save()
        # making a profile for previous user
        profile = Profile.objects.create(
            user=guest,
        )
        profile.save()
        token = Token.objects.create(
            user=guest
        )
        token.save()
        # preparing and sending result to client
        # TODO this message must be encrypted
        message = {'token': token.token,'guest':guest.username }

        return JsonResponse(
            Generator.generate_result(message=message),
        )

    def post(self, request):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('is_encrypted'):
            obj = Generator.generate_dict_from_enc(deserialized_data.get('message'),
                                                   deserialized_data.get('key'))
        else:
            obj = deserialized_data.get('message')

        # Navigating through 'guest info' in message part of data and try to update it
        guest_token = obj.get('token')
        guest_field = obj.get('field')
        guest_grade = obj.get('grade')

        try:
            # guest = User.objects.get(token=guest_token)
            # if Token.objects.filter(token=guest_token).exists():
            guest_token = Token.objects.filter(token=guest_token).get()
            guest_user = guest_token.user

        except User.DoesNotExist:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_token),
            )

        # updating guest information
        # guest.profile.field = guest_field
        # guest.profile.grade = guest_grade
        # guest.save()

        Profile.objects.filter(user=guest_user).update(
            user=guest_user,
            field=guest_field,
            grade=guest_grade,
            guest=True,
        )


        # preparing and sending result to client
        return JsonResponse(
            Generator.generate_result(result_code=constant.success),
        )

# ************************************************************************************************

def generate_private_key(request):
    RSAEncryption().generate_keys()
    return HttpResponse("Generated Successfully")
###################################################################################################
@method_decorator(csrf_exempt, name='dispatch')
class CityList(View):
    def post(self, request, *args, **kwargs):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('is_encrypted'):
            obj = Generator.generate_dict_from_enc(deserialized_data.get('message'),
                                                   deserialized_data.get('key'))
        else:
            obj = deserialized_data.get('message')

        province = obj.get('province')

        city_list = City.objects.filter(province=province)

        result = [{"city_id": city.id, "city": city.city} for city in city_list]

        return JsonResponse(
            Generator.generate_result(result_code=constant.success, message=result),
        )