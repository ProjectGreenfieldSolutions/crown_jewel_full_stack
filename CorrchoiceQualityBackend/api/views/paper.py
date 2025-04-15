# Django application relevant
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

# Application logging creation
from local.Logging import Logger

logger = Logger(__file__)

# Custom Exceptions - Developer Created
from CustomExceptions import UnacceptableActionError, UnexpectedKeyError, InvalidTable

# Progress database fetching
from ..services.ProgressTableReads import ProgressTableReads

# Django database models
from ..models.Account import Account
from ..models.TestEntry import PaperTest, LithoPaperTest
from ..models.Templates import Plant
from ..models.Tracking import Roll, LithoPaper
from ..models.Utility import Grade, PaperType, PaperTestType, Litho

# Django database query functions
from django.db.models import Q, F, Value, CharField, DecimalField, IntegerField, DateField

# Relevant python libraries
import statistics
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
import re
from itertools import chain


# Paper Tests - Paper Tests
@api_view(['GET', 'POST'])
def FetchPaperTests(request):
    logger.info(request.POST)
    request_dict = request.POST

    # Correlate all request parameters to function variables
    plant_object = Plant.objects.filter(code=request_dict.get("plant", "ms")).first() # Default to "ms" if no plant provided
    username_object = Account.objects.filter(username=request_dict["username"]).first()
    target_uuid = request_dict.get("roll_no", [None])

    # Function variables
    current_roll_no = None
    current_litho_uuid = None
    all_plant_objects = Plant.objects.all()
    test_type_headers = []  # Prime the Paper Test Type Headers
    formatted_results = []
    results_row = -1

    # Grab paper test types from the plant being passed into the query
    paper_test_types = PaperTestType.objects.filter(plant=plant_object).order_by("code")

    # Return error message if username doesn't existing in the system.
    if not username_object:
        return JsonResponse({"status": "failed",
                             "message": f"Username {username_object.name} not in system"}, safe=False)

    ########################################################################
    # REGULAR EXPRESSION
    ########################################################################
    # pattern_match = re.match(rf"^LL(\d{{7}})([A-Za-z]+)$", target_uuid)
    # First layer of regular expression logic
    # Layer One: rf"^LL\d{{7}}[A-Za-z]+$"
    # raw format for... string starts with "LL", followed by "seven digits", ending with one+ alphabetic char
    # Second layer
    # Layer Two: rf"^LL(\d{{7}})([A-Za-z]+)$"
    # Addition of () to utilize capture groups, needed for processing the plant code for verification
    # Example Usage: pattern_match.group(2) == "MS"
    ########################################################################
    # if pattern_match:
    #     found_match = False
    #     logger.info("Litho Paper entry detected")
    #     # Return error message if plant code doesn't exist within the system.
    #     for plant in all_plant_objects:
    #         if plant.code.upper() == pattern_match.group(2).upper():
    #             found_match = True
    #             logger.info("Found matching plant code")
    #             query_test_entry_type = "litho_paper"
    #             break
    #
    #     # Invalid plant code passed through the Litho UUID
    #     if not found_match:
    #         return JsonResponse({"status": "failed",
    #                              "message": f"Litho entry {target_uuid} doesn't contain a valid plant code {pattern_match.group(2)}"},
    #                             safe=False)

    for type in paper_test_types:
        test_type_headers.append(type.code + "_count")
        test_type_headers.append(type.code + "_values")
        test_type_headers.append(type.code + "_average")
        test_type_headers.append(type.code + "_standard_deviation")

    paper_tests = PaperTest.objects.select_related("roll", "author", "plant").prefetch_related("roll__grade",
                                                                                               "roll__paper_type",
                                                                                               "test_type")
    litho_paper_tests = LithoPaperTest.objects.select_related("litho_paper", "author", "plant").prefetch_related(
        "test_type")

    roll_filters = Q()
    litho_filters = Q()

    if request_dict:
        if "roll_no" in request_dict:
            logger.info("roll_no detected")
            rolls = Roll.objects.filter(roll_no__contains=target_uuid)
            if rolls.exists():
                logger.info(f"{rolls.count()} rolls found!")
                roll_filters &= Q(roll__in=rolls)
            else:
                roll_filters &= Q(roll=None)

            logger.info("litho_uuid detected")
            litho_papers = LithoPaper.objects.filter(litho_uuid__contains=target_uuid)
            if litho_papers.exists():
                logger.info(f"{litho_papers.count()} litho papers found!")
                litho_filters &= Q(litho_paper__in=litho_papers)
            else:
                litho_filters &= Q(litho_paper=None)

        if "author" in request_dict:
            logger.info("author detected")
            author = Account.objects.filter(username=request_dict["author"]).first()
            if author:
                logger.info("author found")
                roll_filters &= Q(author=author)

        if 'start_date' in request_dict and 'end_date' in request_dict:
            logger.info("start/end date detected")
            # Between dates
            start_date = datetime.strptime(request_dict['start_date'], '%Y-%m-%d')
            # Obtains the last possible microsecond of the target date
            end_date = datetime.strptime(request_dict['end_date'], '%Y-%m-%d') + timedelta(days=1) - timedelta(
                microseconds=1)
            logger.info(end_date)
            roll_filters &= Q(created_at__range=(start_date, end_date))
        elif 'start_date' in request_dict:
            logger.info("start date detected")
            # after start date
            start_date = datetime.strptime(request_dict['start_date'], '%Y-%m-%d')
            roll_filters &= Q(created_at__gte=start_date)
        elif 'end_date' in request_dict:
            logger.info("end date detected")
            # before end date
            # Obtains the last possible microsecond of the target date
            end_date = datetime.strptime(request_dict['end_date'], '%Y-%m-%d') + timedelta(days=1) - timedelta(
                microseconds=1)
            roll_filters &= Q(created_at__lte=end_date)

        if 'plant' in request_dict:
            logger.info("plant detected")
            roll_filters &= Q(plant=plant_object)

        if 'grade' in request_dict:
            logger.info("grade detected")
            grade = Grade.objects.filter(code=request_dict['grade']).first()
            if grade:
                logger.info("grade found")
                roll_filters &= Q(roll__grade=grade)

        if 'type' in request_dict:
            logger.info("type detected")
            type = PaperType.objects.filter(code=request_dict['type']).first()
            if type:
                logger.info("type found")
                roll_filters &= Q(roll__paper_type=type)
        # TODO - Add fields for upper management (costs per ton etc...)

    # Apply the filters
    paper_tests = paper_tests.filter(roll_filters)
    litho_paper_tests = litho_paper_tests.filter(litho_filters)
    paper_tests = paper_tests.annotate(
        test_author=F("author__username"),
        roll_width=F("roll__width"),
        roll_cost_msf=F("roll__cost_by_msf"),
        roll_cost_ton=F("roll__cost_by_ton"),
        roll_grade=F("roll__grade__code"),
        roll_type=F("roll__paper_type__code"),
        roll_mill=F("roll__mill"),
        roll_moisture=F("roll__moisture"),
        roll_linear_foot=F("roll__linear_foot"),
        roll_msf=F("roll__msf"),
        roll_weight=F("roll__weight"),
        roll_received_date=F("roll__received_date"),
        roll_no=F("roll__roll_no"),
        roll_tally_id=F("roll__tally_id"),
        roll_vendor_name=F("roll__vendor__desc"),
        roll_vroll_no=F("roll__vroll_no"),
        roll_plant=F("roll__plant__desc"),
        # paper_type_desc is blank
        paper_test_type=F("test_type__code"),
        litho_uuid=Value(None, output_field=CharField()),
        litho_pt=Value(None, output_field=CharField()),
    )

    litho_paper_tests = litho_paper_tests.annotate(
        test_author=F("author__username"),
        roll_width=Value(None, output_field=DecimalField()),
        roll_cost_msf=Value(None, output_field=DecimalField()),
        roll_cost_ton=Value(None, output_field=DecimalField()),
        roll_grade=Value(None, output_field=CharField()),
        roll_type=Value(None, output_field=CharField()),
        roll_mill=Value(None, output_field=CharField()),
        roll_moisture=Value(None, output_field=DecimalField()),
        roll_linear_foot=Value(None, output_field=IntegerField()),
        roll_msf=Value(None, output_field=DecimalField()),
        roll_weight=Value(None, output_field=IntegerField()),
        roll_received_date=Value(None, output_field=DateField()),
        roll_no=Value(None, output_field=CharField()),
        roll_tally_id=Value(None, output_field=CharField()),
        roll_vendor_name=Value(None, output_field=CharField()),
        roll_vroll_no=Value(None, output_field=CharField()),
        roll_plant=F("litho_paper__plant__desc"),
        # paper_type_desc is blank
        paper_test_type=F("test_type__code"),
        litho_uuid=F("litho_paper__litho_uuid"),
        litho_pt=F("litho_paper__litho_pt"),
    )

    # Merge the two separate table records together
    results = chain(paper_tests.values(
        "id", "roll_width", "roll_cost_msf", "roll_cost_ton", "roll_grade", "roll_type", "roll_mill",
        "roll_moisture", "roll_linear_foot", "roll_msf", "roll_weight", "roll_received_date", "roll_no",
        "roll_tally_id", "roll_vendor_name", "roll_vroll_no", "roll_plant", "paper_test_type", "test_author",
        "litho_uuid", "litho_pt", "test_value", "created_at"
    ), litho_paper_tests.values(
        "id", "roll_width", "roll_cost_msf", "roll_cost_ton", "roll_grade", "roll_type", "roll_mill",
        "roll_moisture", "roll_linear_foot", "roll_msf", "roll_weight", "roll_received_date", "roll_no",
        "roll_tally_id", "roll_vendor_name", "roll_vroll_no", "roll_plant", "paper_test_type", "test_author",
        "litho_uuid", "litho_pt", "test_value", "created_at"
    ))

    for r in results:
        logger.info(r)
        # Reset calculation variables
        test_average_value = None

        # Get current paper type column name
        test_count_column_name = r["paper_test_type"] + "_count"
        test_value_column_name = r["paper_test_type"] + "_values"
        test_average_column_name = r["paper_test_type"] + "_average"
        test_stdev_column_name = r["paper_test_type"] + "_standard_deviation"

        # Append all paper test types to row
        for type in test_type_headers:
            if "values" in type:
                r[type] = None
            elif "count" in type:
                r[type] = None
            else:
                r[type] = None

        # Is this the same roll/litho uuid?
        if f"{r['roll_no']}" == f"{current_roll_no}" and f"{r['litho_uuid']}" == f"{current_litho_uuid}":
            logger.info("Existing roll detected...")
            # Is this the same paper test type?
            # Prime the values required for test count / test value / test average
            if not test_count_column_name in formatted_results[results_row]:
                formatted_results[results_row][test_count_column_name] = 1
                formatted_results[results_row][test_value_column_name] = f"{r['test_value']}"
                formatted_results[results_row][test_average_column_name] = r["test_value"]
                formatted_results[results_row][test_stdev_column_name] = Decimal(0.0)

            if formatted_results[results_row][test_count_column_name] != 0:
                formatted_results[results_row][test_count_column_name] = formatted_results[results_row][
                                                                             test_count_column_name] + 1 if not formatted_results[results_row][test_count_column_name] is None else 1
                formatted_results[results_row][test_value_column_name] = formatted_results[results_row][test_value_column_name] + "," + f"{r['test_value']}" if not formatted_results[results_row][test_value_column_name] is None else  f"{r['test_value']}"

                for value in formatted_results[results_row][test_value_column_name].split(","):
                    if not test_average_value:
                        # Initial assignment
                        test_average_value = 0.0
                    test_average_value += float(value)

                formatted_results[results_row][test_average_column_name] = test_average_value / float(
                    formatted_results[results_row][
                        test_count_column_name])

                if not formatted_results[results_row][test_stdev_column_name] is None:
                    formatted_results[results_row][test_stdev_column_name] = statistics.stdev(
                    [Decimal(value) for value in formatted_results[results_row][test_value_column_name].split(",")])

                # Remove value export
                if formatted_results[results_row][test_stdev_column_name] == 0.0:
                    formatted_results[results_row][test_stdev_column_name] = None
        else:
            logger.info("New roll detected...")
            # Useful variables
            current_roll_no = r["roll_no"]
            current_litho_uuid = r["litho_uuid"]

            # Set the starter values
            r[test_count_column_name] = 1
            r[test_value_column_name] = f"{r['test_value']}"
            r[test_average_column_name] = r["test_value"]
            r[test_stdev_column_name] = ""

            # Format the date to be more human friendly
            date_string = datetime.strptime(str(r["created_at"]).split(" ")[0], "%Y-%m-%d")
            r["year"] = date_string.year
            r["month"] = date_string.month
            r["day"] = date_string.day
            if r["roll_type"]:
                r["roll_type"] = r["roll_type"].upper()
            # r["test_type"] = r["paper_test_type"]
            formatted_results.append(r)
            results_row += 1

        # Reformatting datetime
        r["created_at"] = str(r["created_at"].date())

        # Remove if not supervisor
        if not username_object.is_supervisor:
            del r["roll_cost_msf"]
            del r["roll_cost_ton"]
        else:
            # Re-assigned here to relocate the columns on the export to the end
            r["cost_by_ton"] = r["roll_cost_ton"]
            r["cost_by_msf"] = r["roll_cost_msf"]
            del r["roll_cost_msf"]
            del r["roll_cost_ton"]

        # Remove unneeded fields
        del r["paper_test_type"]
        del r["test_value"]

    payload = {
        "status": "success",
        "message": "",
        "formatted_results": formatted_results,
    }
    return JsonResponse(payload, safe=False)


# Paper Tests - Paper Tests
@api_view(['GET', 'POST'])
def FetchRollPaperTestEntries(request):
    request_dict = request.POST
    logger.info(message=f"request_dict={request_dict}")

    if request_dict == {}:
        logger.info(message=f"Empty request_dict")
        results = PaperTest.objects.all()
    else:
        logger.info(message=f"Non-empty request_dict")
        plant_object = Plant.objects.filter(code=request_dict["plant"]).first()
        roll_object = Roll.objects.filter(plant=plant_object, roll_no=request_dict["roll_no"]).first()
        results = PaperTest.objects.filter(plant=plant_object, roll=roll_object)

    list_of_results = []

    for r in results:
        list_of_results.append({
            "id": r.id,
            "roll_no": r.get_roll_no(),
            "test_type": r.get_test_type_desc(),
            "test_position": r.get_test_position_desc(),
            "test_reason": r.get_test_reason_desc(),
            "test_value": r.test_value,
        })

    return JsonResponse(list_of_results, safe=False)


# Paper Tests - Paper Tests
@api_view(['GET', 'POST'])
def FetchLithoPaperTestEntries(request):
    request_dict = request.POST
    logger.info(message=f"request_dict={request_dict}")

    if request_dict == {}:
        logger.info(message=f"Empty request_dict")
        results = LithoPaperTest.objects.all()
    else:
        logger.info(message=f"Non-empty request_dict")
        plant_object = Plant.objects.filter(code=request_dict["plant"]).first()
        litho_paper_object = LithoPaper.objects.filter(plant=plant_object,
                                                       litho_uuid=request_dict["litho_uuid"]).first()
        results = LithoPaperTest.objects.filter(plant=plant_object, litho_paper=litho_paper_object).all()

    list_of_results = []

    logger.info(f"Looping through all results {results}")
    for r in results:
        logger.info(f"Looping for UUID={r.get_litho_paper_uuid()} | VALUE={r.test_value} | PT={r.get_litho_paper_pt()}")
        list_of_results.append({
            "id": r.id,
            "litho_uuid": r.get_litho_paper_uuid(),
            "litho_pt": r.get_litho_paper_pt(),
            "test_position": r.get_test_position_desc(),
            "test_reason": r.get_test_reason_desc(),
            "test_type": r.get_test_type_desc(),
            "test_value": r.test_value,
            "plant_code": r.get_plant_code().upper(),
        })

    return JsonResponse(list_of_results, safe=False)


# Paper Test Entry - Search Roll
@api_view(['GET', 'POST'])
def PaperSearchRoll(request):
    # TODO - Manually cause a timeout and determine how to send a response code of 111
    request_dict = request.POST
    payload_dict = {}

    for key in request_dict:
        payload_dict[key] = request_dict[key]

    payload_dict["action"] = "find_rolls"

    # Query the Progress database for the relevant information
    try:
        results = ProgressTableReads(payload=payload_dict)
    except UnexpectedKeyError as e:
        logger.error(message=f"{e}", details="Paper Test Entry - Search Rolls")
        error = {"Error": "UnexpectedKeyError", "Message": str(e)}
        return JsonResponse(error)
    except UnacceptableActionError as e:
        logger.error(message=f"Exception = {e}", details="Paper Test Entry - Search Rolls")
        error = {"Error": "UnacceptableActionError", "Message": str(e)}
        return JsonResponse(error)
    except Exception as e:
        logger.error(message=f"Exception = {e}", details="Paper Test Entry - Search Rolls")
        error = {"Error": "Exception", "Message": str(e)}
        return JsonResponse(error)
    else:
        return JsonResponse(results)


# Paper Test Entry - Search Litho
@api_view(['GET', 'POST'])
def PaperSearchLitho(request):
    request_dict = request.POST
    logger.info(request_dict)

    def generate_unique_seven_digit():
        while True:
            value = int(uuid.uuid4().int >> 64) % 10000000
            if value > 999999:
                return value

    # Generate a unique id
    plant_object = Plant.objects.get(code=request_dict["plant"])

    if request_dict["litho_uuid"].lower() == "litho":
        logger.info("New litho number needed")
        while True:
            uuid_value = generate_unique_seven_digit()
            uuid_plant_record = "LL" + str(uuid_value) + request_dict["plant"].upper()
            if not LithoPaper.objects.filter(plant=plant_object, litho_uuid=uuid_plant_record).exists():
                new_litho_paper_object = LithoPaper(plant=plant_object, litho_uuid=uuid_plant_record)
                results = {0: {"litho_uuid": new_litho_paper_object.litho_uuid,
                               "litho_pt": str(new_litho_paper_object.litho_pt) + "PT",
                               "created_at": str(new_litho_paper_object.created_at),
                               "plant_code": str(new_litho_paper_object.plant.code).upper()}}
                # new_litho_paper_object.save()
                break
    else:
        logger.info("Find an existing litho number")
        if not LithoPaper.objects.filter(plant=plant_object, litho_uuid=request_dict["litho_uuid"]).exists():
            error = {"status": "error",
                     "message": f"No litho paper value with {request_dict['litho_uuid']} could be found"}
            return JsonResponse(error)
        litho_paper_object = LithoPaper.objects.get(plant=plant_object, litho_uuid=request_dict["litho_uuid"])
        results = {0: {"litho_uuid": litho_paper_object.litho_uuid,
                       "litho_pt": str(litho_paper_object.litho_pt) + "PT",
                       "created_at": str(litho_paper_object.created_at).split(" ")[0],
                       "plant_code": str(litho_paper_object.plant.code).upper()
                       }}

    results["status"] = "success"
    results["message"] = "Results successfully fetched from server!"
    logger.info(results)
    return JsonResponse(results)
