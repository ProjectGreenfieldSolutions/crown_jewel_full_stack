from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from ..services.ProgressTableReads import ProgressTableReads
from ..services.ProgressConnections import AuthenticationManager
from ..models.Account import Account

from local.Logging import Logger

logger = Logger(__file__)

from CustomExceptions import UnacceptableActionError, UnexpectedKeyError, InvalidTable

@api_view(["POST"])
def Authenticate(request):
    # Collect payload input
    req = request.POST
    username = req["username"]
    password = req["password"]
    plant = req["plant"]

    obj = AuthenticationManager(username, password, plant)
    # Send payload to Progress

    return JsonResponse({"query": obj.authenticate()})


@api_view(['POST'])
def Login(request):
    payload_dict = request.POST
    username = payload_dict['username']
    password = payload_dict['password']

    results = {}
    logger.info(message=f"username = {username} | password = {password}", details=f"Login VIEW")

    user = Account.objects.filter(username=username)[0]
    if user.check_password(password):
        logger.info(message=f"User authenticated {username}... returning user")
        logger.info(user)
        results = {
            "username": user.username,
            "email": user.email,
            "first_name": user.get_short_name(),
            "full_name": user.get_full_name(),
            "session": "",
        }
    else:
        error = "User not authenticated"
        logger.info(message=f"{error}")
        results = {
            "error": error
        }

    return JsonResponse(results)


@api_view(['POST'])
def Registration(request):
    payload_dict = request.POST
    # try:
    #   results = ProgressConnection(payload=payload_dict)
    # except UnexpectedKeyError as e:
    #   logger.error(message=f"{e}", details=f"Action = {payload_dict['action']}")
    #   error = {"Error": "UnexpectedKeyError", "Message": str(e)}
    #   return JsonResponse(error)
    # except UnacceptableActionError as e:
    #   logger.error(message=f"Exception = {e}", details=f"Action = {payload_dict['action']}")
    #   error = {"Error": "UnacceptableActionError", "Message": str(e)}
    #   return JsonResponse(error)
    # except Exception as e:
    #   logger.error(message=f"Exception = {e}", details=f"Action = {payload_dict['action']}")
    #   error = {"Error": "Exception", "Message": str(e)}
    #   return JsonResponse(error)
    # else:
    #   return JsonResponse(results)


@api_view(['POST'])
def Logout(request):
    payload_dict = request.POST
    # try:
    #   results = ProgressConnection(payload=payload_dict)
    # except UnexpectedKeyError as e:
    #   logger.error(message=f"{e}", details=f"Action = {payload_dict['action']}")
    #   error = {"Error": "UnexpectedKeyError", "Message": str(e)}
    #   return JsonResponse(error)
    # except UnacceptableActionError as e:
    #   logger.error(message=f"Exception = {e}", details=f"Action = {payload_dict['action']}")
    #   error = {"Error": "UnacceptableActionError", "Message": str(e)}
    #   return JsonResponse(error)
    # except Exception as e:
    #   logger.error(message=f"Exception = {e}", details=f"Action = {payload_dict['action']}")
    #   error = {"Error": "Exception", "Message": str(e)}
    #   return JsonResponse(error)
    # else:
    #   return JsonResponse(results)

