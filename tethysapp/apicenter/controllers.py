from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import Button

@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {
    }
    return render(request, 'apicenter/introduction.html', context)

def purpose(request):
    context = {
    }
    return render(request, 'apicenter/purpose.html', context)

def Registration(request):
    context = {
    }
    return render(request, 'apicenter/Registration.html', context)

def ECMWFAPIService(request):
    context = {
    }
    return render(request, 'apicenter/ECMWF_API_Service.htm', context)

def HIWATAPIService(request):
    context = {
    }
    return render(request, 'apicenter/HIWATAPIService.html', context)

def ECMWF_API_service_Get_Forecast_Data(request):
    context = {
    }
    return render(request, 'apicenter/ECMWF_API_service_Get_Forecast_Data.html', context)

def ECMWF_API_service_Get_Historic_Data(request):
    context = {
    }
    return render(request, 'apicenter/ECMWF_API_service_Get_Historic_Data.html', context)

def HIWATAPIService_Get_Historic_Data(request):
    context = {
    }
    return render(request, 'apicenter/HIWATAPIService_Get_Historic_Data.html', context)

def HIWATAPIService_Get_Return_periods(request):
    context = {
    }
    return render(request, 'apicenter/HIWATAPIService_Get_Return_periods.html', context)

def HIWATAPIService_Get_Forecast_data(request):
    context = {
    }
    return render(request, 'apicenter/HIWATAPIService_Get_Forecast_data.html', context)

def HIWATAPIService_Get_ID_of_Stream(request):
    context = {
    }
    return render(request, 'apicenter/HIWATAPIService_Get_ID_of_Stream.html', context)


from rest_framework.views import APIView
from rest_framework import serializers,exceptions
from django.contrib.auth import authenticate
from rest_framework.generics import get_object_or_404
from django.contrib.auth import login as django_login
from rest_framework.authtoken.models import Token
from django.middleware.csrf import get_token
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.models import User
def validateEmail( email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False


class LoginSerializer(serializers.Serializer):
    UserNameOrEmail=serializers.CharField()
    Password=serializers.CharField()

    def validate(self, data):
        UserNameOrEmail = data.get('UserNameOrEmail', None)
        Password=data.get("Password", None)

        if UserNameOrEmail and Password:
            if validateEmail(UserNameOrEmail):
                user_request = get_object_or_404(
                    User,
                    email=UserNameOrEmail,
                )
                UserNameOrEmail = user_request.username

            user=authenticate(username=UserNameOrEmail,password=Password)
            if user:
                if user.is_active:
                    data["user"]=user
                else:
                    msg="User is disabled."
                    raise exceptions.ValidationError(msg)
            else:
                msg='Unable to login with given credentials.'
                raise exceptions.ValidationError(msg)

        else:
            msg="Must provide username and password both."
            raise exceptions.ValidationError(msg)
        return data





class LoginView(APIView):
    def post(self, request):
        # print(request.data)
        # csrfToken=get_token(request)
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        django_login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        token, created = Token.objects.get_or_create(user=user)
        return Response({"Token": token.key,
                         "UserName": user.username,
                         "Email": user.email,
                         "FirstName": user.first_name,
                         "LastName": user.last_name }, status=200)


def GetToken(request):

    a=User.objects.get(username='demo')
    from django.contrib.auth import login as django_login
    django_login(request, a, backend='django.contrib.auth.backends.ModelBackend')
    token, created = Token.objects.get_or_create(user=a)
    return JsonResponse({"hello":"hello","token":str(token)})
