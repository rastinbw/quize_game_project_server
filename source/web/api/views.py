from django.contrib.auth.models import User
from web.models import Token, Profile, Guest
from web.helpers import RSAEncryption, Generator, JsonResponse, AESEncryption
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import web.consts as constant


@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request, *args, **kwargs):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
                status="400",
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
                status="400",
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('is_encrypted'):
            obj = Generator.generate_dict_from_enc(deserialized_data.get('message'),
                                                   deserialized_data.get('key'))
        else:
            obj = deserialized_data.get('message')

        # Navigating through 'user info' in message part of data and save it into database
        username = obj.get('username')
        email = obj.get('email', '')
        password = obj.get('password')

        city_id = obj.get('city_id')
        phone_number = obj.get('phone_number', '')

        # Check whether input username is already in database or not
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                Generator.generate_result(result_code=constant.repetitive_username),
                status="400",
            )

        # Check whether input email is already in database or not
        if email != '' and User.objects.filter(email=email).exists():
            return JsonResponse(
                Generator.generate_result(result_code=constant.repetitive_email),
                status="400",
            )

        # Check whether input phone number is already in database or not
        if phone_number != '' and Profile.objects.filter(phone_number=phone_number).exists():
            return JsonResponse(
                Generator.generate_result(result_code=constant.repetitive_phone_number),
                status="400",
            )

        # saving user in database
        user = User.objects.create(
            username=username,
            password=password,
            email=email,
        )
        user.save()

        # making a profile for previous user
        profile = Profile.objects.create(
            user=user,
            cityId=city_id,
            phoneNumber=phone_number,
        )
        profile.save()

        # creating a token for previous user
        token = Token.objects.create(user=user)
        token.save()

        # preparing and sending result to client
        # TODO this message must be encrypted
        message = {'token': token.token, }

        return JsonResponse(
            Generator.generate_result(message=message, key=deserialized_data.get('key')),
            status=200,
        )


@method_decorator(csrf_exempt, name='dispatch')
class Login(View):
    def post(self, request, *args, **kwargs):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
                status="400",
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
                status="400",
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('isEncrypted'):
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
                status="400",
            )

        # Check whether user with input username/password exists in database
        if username != '':
            try:
                user = User.objects.get(username=username, password=password)
            except User.DoesNotExist:
                return JsonResponse(
                    Generator.generate_result(result_code=constant.wrong_username_and_password),
                    status="400",
                )

        # Check whether user with input email/password exists in database
        else:
            try:
                user = User.objects.get(email=email, password=password)
            except User.DoesNotExist:
                return JsonResponse(
                    Generator.generate_result(result_code=constant.wrong_email_and_password),
                    status="400",
                )

        # preparing and sending result to client
        # TODO this message must be encrypted
        message = {'token': user.token.token, }

        return JsonResponse(
            Generator.generate_result(message=message, key=deserialized_data.get('key')),
            status=200,
        )


@method_decorator(csrf_exempt, name='dispatch')
class GuestRegister(View):
    def get(self, request):
        """
        this view creates a guest and
        returns the generated guest uuid for
        authentication to client
        """
        guest = Guest.objects.create()

        # preparing and sending result to client
        # TODO this message must be encrypted
        message = {'guest_id': guest.guest_id, }

        return JsonResponse(
            Generator.generate_result(message=message),
            status=200,
        )

    def post(self, request):
        # Check whether required data is provided or not
        if not request.POST:
            return JsonResponse(
                Generator.generate_result(result_code=constant.no_data_provided),
                status="400",
            )

        # Get the provided json data and try to deserialize it to python dictionary
        data = request.POST.get('data')
        try:
            deserialized_data = json.loads(data)
        except ValueError:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_json_format),
                status="400",
            )

        # Decrypt message in deserialized_data body if its encrypted
        if deserialized_data.get('is_encrypted'):
            obj = Generator.generate_dict_from_enc(deserialized_data.get('message'),
                                                   deserialized_data.get('key'))
        else:
            obj = deserialized_data.get('message')

        # Navigating through 'guest info' in message part of data and try to update it
        guest_id = obj.get('guest_id')
        guest_field = obj.get('guest_field')
        guest_grade = obj.get('guest_grade')

        try:
            guest = Guest.objects.get(guest_id=guest_id)
        except Guest.DoesNotExist:
            return JsonResponse(
                Generator.generate_result(result_code=constant.invalid_guest_id),
                status="400",
            )

        # updating guest information
        guest.guest_field = guest_field
        guest.guest_grade = guest_grade
        guest.save()

        # preparing and sending result to client
        return JsonResponse(
            Generator.generate_result(result_code=constant.success),
            status=200,
        )

# ************************************************************************************************

def generate_private_key(request):
    RSAEncryption().generate_keys()
    return HttpResponse("Generated Successfully")


@method_decorator(csrf_exempt, name='dispatch')
class Test(View):
    def post(self, request):
        d = request.POST.get('data')
        try:
            data = json.loads(d)
        except ValueError:
            return HttpResponse({'Error': "Invalid json format"}, status="400")

        obj = Generator.generate_dict_from_enc(data.get('message'), data.get('key'))
        return HttpResponse(Generator.generate_result(obj))


@csrf_exempt
def test(request):
    # data = request.POST.get('data')
    #
    # try:
    #     data = json.loads(data)
    # except ValueError:
    #     return Response({'Error': "Invalid json format"}, status="400")
    #
    # rsa = ProductionEncryption()
    # drd = rsa.decrypt(encoded_encrypted_message=data.get('key'))
    #
    # key = drd[0:16]
    # iv = drd[16:32]
    #
    # mode = AES.MODE_CBC
    # decryptor = AES.new(key, mode, IV=iv)
    # obj = decryptor.decrypt(data.get('message'))

    return HttpResponse("xxxxxxfuckxxxxxxxxxxxxxx")




