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
import json

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


@api_view(["POST"])
def InitAccount(request):
    """
    Procedures to execute during first login
    """
    payload = request.POST
    username = payload["username"]
    password = payload["password"]
    plant = payload["plant"]
    preferences = json.loads(payload["preferences"])

    if Account.objects.filter(username=username).exists():
        logger.info(message=f"account exists")
        user = Account.objects.filter(username=username).first()

        # Note: if you add another layer to this, use the following code to find the coupled code. (nested_nested_nested_key)
        # Resource: If need, https://www.freecodecamp.org/news/how-to-flatten-a-dictionary-in-python-in-4-different-ways/
        ## Note: The subsequent for loops are meant to ONLY copy over the template key if its NOT already present. Enabling
        ## the ability to add new keys should the application change
        for outer_key in preferences.keys():
            if not outer_key in user.preferences.keys():
                logger.info(f"adding {outer_key} to user.prefer")
                user.preferences[outer_key] = preferences[outer_key]

            try:
                user.preferences[outer_key].keys()
            except:
                continue

            for second_key in preferences[outer_key].keys():
                if not second_key in user.preferences[outer_key].keys():
                    logger.info(f"adding {second_key} to user.prefer")
                    user.preferences[outer_key][second_key] = preferences[outer_key][second_key]

                try:
                    user.preferences[outer_key][second_key].keys()
                except:
                    continue

                for third_key in preferences[outer_key][second_key].keys():
                    if not third_key in user.preferences[outer_key][second_key].keys():
                        logger.info(f"adding {third_key} to user.prefer")
                        user.preferences[outer_key][second_key][third_key] = preferences[outer_key][second_key][
                            third_key]

        # Update preferences, if there aren't any keys associated with this user
        user.save(update_fields=["preferences"])

        # Is user active?
        if user.is_active:
            logger.info(message=f"exists, active")
            # Get account type
            if user.is_admin:
                type = "admin"
            elif user.is_supervisor:
                type = "supervisor"
            else:
                type = "user"

            results = {
                "authenticated": True,
                "username": user.username,
                "plant": user.home_plant,
                "type": type,
                "preferences": user.preferences,
            }

        else:
            logger.info(message=f"exists, not active")
            # User not active
            results = {
                "authenticated": False,
                "type": False,
                "preferences": {},
            }
    else:
        logger.info(message=f"user doesn't exist")
        # User doesn't exist
        # Create user
        user = Account.objects.create_user(username=username, password=password)

        # Assign account type
        default_admins = ["ktc"]
        if username.lower() in default_admins:
            user.is_admin = True
            user.is_supervisor = True

        # Assign home plant
        user.home_plant = plant

        # Assign default preferences
        user.preferences = json.loads(payload["preferences"])

        # Commit user to django database
        user.save()

        # Creation was successful?
        if user:
            logger.info(message=f"creation user success {user}")
            type = ""
            if user.is_admin:
                type = "admin"
            elif user.is_supervisor:
                type = "supervisor"
            else:
                type = "user"

            results = {
                "authenticated": True,
                "username": user.username,
                "plant": user.home_plant,
                "type": type,
                "preferences": user.preferences,
            }
        # Creation failed
        else:
            logger.critical(message=f"User creation failed hard payload={payload}")
            # User not active
            results = {
                "authenticated": False,
                "type": False,
                "preferences": {},
            }

    logger.info(f"Returning results={results}")
    return JsonResponse(results)


@api_view(["POST"])
def GetAccountData(request):
    logger.info("GetAccountData")
    payload = request.POST
    username = Account.objects.filter(username=payload["username"]).first()
    # Note: Superuser is a Django default
    if username.is_admin or username.is_superuser:
        list_of_accounts = []
        accounts = Account.objects.all()
        for user in accounts:
            list_of_accounts.append(
                {"username": user.username, "is_active": user.is_active, "is_supervisor": user.is_supervisor,
                 "is_admin": user.is_admin})
        return JsonResponse({"status": "success", "message": "Account records fetched", "records": list_of_accounts})
    else:
        return JsonResponse({"status": "failure", "message": "You may not view this table", "records": []})

@api_view(["POST"])
def UpdateAccountData(request):
    logger.info("UpdateAccountData")
    payload = request.POST
    logger.info(payload)
    user_to_update = Account.objects.filter(username=payload["username"]).first()
    if user_to_update:
        user_to_update.is_active = payload["is_active"]
        user_to_update.is_supervisor = payload["is_supervisor"]
        user_to_update.is_admin = payload["is_admin"]
        user_to_update.save()
        return JsonResponse({"status": "success",
                             "message": f"Updating user {user_to_update.username} with values is_active={user_to_update.is_active}, is_supervisor={user_to_update.is_supervisor}, is_admin={user_to_update.is_admin}"})
    else:
        return JsonResponse({"status": "failure", "message": "username could not be found in the system"})


@api_view(['POST'])
def UpdatePreferences(request):
    logger.info("Updating user preferences")
    payload = json.loads(request.body)
    user = Account.objects.filter(username=payload.get("username")).first()
    if Account.objects.filter(username=payload.get("username")).exists:
        logger.info("User does exist, updating preferences")
        user.preferences = payload.get("preferences")
        user.save()
        return JsonResponse({"message": "Updated the user preferences"})
    else:
        return JsonResponse({"message": "User doesn't exist"})


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
