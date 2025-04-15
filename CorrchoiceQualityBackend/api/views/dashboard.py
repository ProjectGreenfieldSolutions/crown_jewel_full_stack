from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.models import User
from ..models.Account import Account
from ..models.Templates import Plant
from ..models.TestEntry import PaperTest, CombinedBoardTest
from django.db.models import Q, F, Count

from local.Logging import Logger
import json

logger = Logger(__file__)

from CustomExceptions import UnacceptableActionError, UnexpectedKeyError, InvalidTable


@api_view(["POST"])
def DashboardData(request):
    # Internal variables
    list_of_appropriate_graphs = ["paper_tests_per_plant", "combined_tests_per_plant"]
    results = {
        "data": [],
        "datetime": None,
    }

    # Collect payload input
    payload = request.POST

    # Check for graph
    graph = payload["graph"]
    if not graph in list_of_appropriate_graphs:
        return JsonResponse({"status": "failure", "message": f"Graph type of {graph} isn't valid.", "results": None})

    # Check for username
    username = payload["username"]
    account = Account.objects.filter(username=username).first()

    if not account:
        return JsonResponse({"status": "failure", "message": f"Username {username} isn't valid.", "results": None})

    if payload["graph"] == "paper_tests_per_plant":
        queryset = PaperTest.objects.filter(Q(plant__gt=0)).distinct()
    elif payload["graph"] == "combined_tests_per_plant":
        queryset = CombinedBoardTest.objects.filter(Q(plant__gt=0)).distinct()
    else:
        Logger.critical(f"Literally should never happen")
        # Writing this just to make me feel better about the yellow highlighting below on line 54
        queryset = PaperTest.objects.all().first()

    plants = Plant.objects.all()
    for plant in plants:
        test_count = queryset.filter(plant__code=plant.code).count()
        # Note: One can just create a new key/value to this, the "browse" widget will display it regardless
        results["data"].append({"plant": plant.desc, "quantity": test_count})

    return JsonResponse({"status": "success", "message": "Dashboard data successfully fetched.", "data": results["data"]})
