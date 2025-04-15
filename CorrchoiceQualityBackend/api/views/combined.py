from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from ..services.ProgressTableReads import ProgressTableReads
from datetime import datetime, timedelta
from copy import deepcopy

from local.Logging import Logger

logger = Logger(__file__)

from CustomExceptions import UnacceptableActionError, UnexpectedKeyError, InvalidTable
from ..models.Account import Account
from ..models.Templates import Plant
from ..models.Tracking import Order
from ..models.TestEntry import CombinedBoardTest
from ..models.Utility import CombinedBoardTestType, Flute, CombinedBoardTestLayer
from django.db.models import Q, F


# Combined Tests - Combined Board Tests
@api_view(['GET', 'POST'])
def FetchCombinedTests(request):
    request_dict = request.POST
    logger.info(request_dict)

    username_object = Account.objects.filter(username=request_dict["username"]).first()
    if not username_object:
        return JsonResponse({"status": "failed",
                             "message": f"Username {username_object.name} not in system"}, safe=False)

    queryset = CombinedBoardTest.objects.select_related("order", "account", "plant").prefetch_related("order__flute",
                                                                                                      "order__order_no",
                                                                                                      "order__test_code")

    filters = Q()

    if request_dict:
        if "order_no" in request_dict:
            logger.info("order_no detected")
            orders = Order.objects.filter(order_no__contains=request_dict["order_no"])
            if orders.exists():
                logger.info(f"{orders.count()} orders found!")
                filters &= Q(order__in=orders)
            else:
                filters &= Q(order=None)

        if "author" in request_dict:
            logger.info("author detected")
            author = Account.objects.filter(username=request_dict["author"]).first()
            if author:
                logger.info("author detected")
                filters &= Q(author=author)

        if 'start_date' in request_dict and 'end_date' in request_dict:
            logger.info("start/end date detected")
            # Between dates
            start_date = datetime.strptime(request_dict['start_date'], '%Y-%m-%d')
            # Obtains the last possible microsecond of the target date
            end_date = datetime.strptime(request_dict['end_date'], '%Y-%m-%d') + timedelta(days=1) - timedelta(microseconds=1)
            filters &= Q(created_at__range=(start_date, end_date))
        elif 'start_date' in request_dict:
            logger.info("start date detected")
            # after start date
            start_date = datetime.strptime(request_dict['start_date'], '%Y-%m-%d')
            filters &= Q(created_at__gte=start_date)
        elif 'end_date' in request_dict:
            logger.info("end date detected")
            # Obtains the last possible microsecond of the target date
            end_date = datetime.strptime(request_dict['end_date'], '%Y-%m-%d') + timedelta(days=1) - timedelta(microseconds=1)
            filters &= Q(created_at__lte=end_date)

        if 'plant' in request_dict:
            logger.info("plant detected")
            plant = Plant.objects.filter(code=request_dict['plant']).first()
            if plant:
                logger.info("plant found")
                filters &= Q(plant=plant)

        if 'flute' in request_dict:
            logger.info("flute detected")
            flute = Flute.objects.filter(code=request_dict['flute']).first()
            if flute:
                logger.info("flute object found")
                filters &= Q(order__flute=flute)

        if 'type' in request_dict:
            logger.info("test detected")
            combinedboardtest = CombinedBoardTestType.objects.filter(code=request_dict['type']).first()
            if combinedboardtest:
                logger.info("type object found")
                filters &= Q(test_type=combinedboardtest)

        # TODO - Add fields for upper management (costs per ton etc...)

    results = queryset.filter(filters).annotate(
        order_no=F("order__order_no"),
        plant_desc=F("plant__desc"),
        test_author=F("author__username"),
        order_corrugator_name=F("order__corrugator__desc"),
        order_customer_name=F("order__customer__desc"),
        order_flute_desc=F("order__flute__desc"),
        order_ship_date=F("order__ship_date"),
        order_test_code=F("order__test_code__code"),
        combined_test_reason=F("test_reason__desc"),

        # Roll Values
        combined_litho_1=F("test_litho_1__desc"),
        combined_roll_1=F("test_roll_1__roll_no"),
        combined_roll_2=F("test_roll_2__roll_no"),
        combined_roll_3=F("test_roll_3__roll_no"),
        combined_roll_4=F("test_roll_4__roll_no"),
        combined_roll_5=F("test_roll_5__roll_no"),
        combined_roll_6=F("test_roll_6__roll_no"),
        combined_roll_7=F("test_roll_7__roll_no"),

        # Layer used
        combined_layer_1=F("test_layer_1__code"),
        combined_layer_2=F("test_layer_2__code"),
        combined_layer_3=F("test_layer_3__code"),
        combined_layer_4=F("test_layer_4__code"),
        combined_layer_5=F("test_layer_5__code"),
        combined_layer_6=F("test_layer_6__code"),
        combined_layer_7=F("test_layer_7__code"),

        # Roll Vendor
        l1_roll_vendor=F("test_roll_1__vendor__desc"),
        l2_roll_vendor=F("test_roll_2__vendor__desc"),
        l3_roll_vendor=F("test_roll_3__vendor__desc"),
        l4_roll_vendor=F("test_roll_4__vendor__desc"),
        l5_roll_vendor=F("test_roll_5__vendor__desc"),
        l6_roll_vendor=F("test_roll_6__vendor__desc"),
        l7_roll_vendor=F("test_roll_7__vendor__desc"),

        # Paper Type used
        l1_roll_paper_type=F("test_roll_1__paper_type__code"),
        l2_roll_paper_type=F("test_roll_2__paper_type__code"),
        l3_roll_paper_type=F("test_roll_3__paper_type__code"),
        l4_roll_paper_type=F("test_roll_4__paper_type__code"),
        l5_roll_paper_type=F("test_roll_5__paper_type__code"),
        l6_roll_paper_type=F("test_roll_6__paper_type__code"),
        l7_roll_paper_type=F("test_roll_7__paper_type__code"),

        # Roll Grade
        l1_roll_grade=F("test_roll_1__grade__code"),
        l2_roll_grade=F("test_roll_2__grade__code"),
        l3_roll_grade=F("test_roll_3__grade__code"),
        l4_roll_grade=F("test_roll_4__grade__code"),
        l5_roll_grade=F("test_roll_5__grade__code"),
        l6_roll_grade=F("test_roll_6__grade__code"),
        l7_roll_grade=F("test_roll_7__grade__code"),

        combined_test_type=F("test_type__desc"),
    ).values("id", "order_no", "plant_desc", "order_corrugator_name",
             "order_customer_name", "order_test_code", "order_flute_desc", "order_ship_date", "combined_test_reason",
             "combined_test_type",
             "combined_litho_1", "combined_layer_1", "combined_roll_1", "combined_layer_2", "combined_roll_2", "combined_layer_3",
             "combined_roll_3", "combined_layer_4", "combined_roll_4", "combined_layer_5", "combined_roll_5",
             "combined_layer_6", "combined_roll_6", "combined_layer_7", "combined_roll_7",
             "test_value", "created_at", "test_author",
             "l1_roll_vendor", "l1_roll_grade", "l1_roll_paper_type",
             "l2_roll_vendor", "l2_roll_grade", "l2_roll_paper_type",
             "l3_roll_vendor", "l3_roll_grade", "l3_roll_paper_type",
             "l4_roll_vendor", "l4_roll_grade", "l4_roll_paper_type",
             "l5_roll_vendor", "l5_roll_grade", "l5_roll_paper_type",
             "l6_roll_vendor", "l6_roll_grade", "l6_roll_paper_type",
             "l7_roll_vendor", "l7_roll_grade", "l7_roll_paper_type",
             )

    # Variables for formatting the output
    template_formatted_row = {}
    current_order = None
    formatted_row = None
    formatted_rows = []
    list_of_combined_test_types = []
    list_of_combined_test_layers = []

    # Get the first plant object, assumes all plants contain the same paper test types
    ## Modify App Records screen updates all plants for any given table
    plant_object = Plant.objects.all().first()
    combined_test_type_objects = CombinedBoardTestType.objects.filter(plant=plant_object).order_by("code")
    all_available_layer_objects = CombinedBoardTestLayer.objects.filter(plant=plant_object).order_by("created_at")
    map_layers_to_record_return = {"l1": "1", "m1": "2", "l2": "3", "m2": "4", "l3": "5", "m3": "6", "l4": "7"}

    for row in results:
        # Copy the row over
        formatted_row = deepcopy(row)
        # Format the date
        date_string = str(row["created_at"])
        formatted_row["created_at"] = date_string[:date_string.find("T")].split(" ")[0]
        formatted_rows.append(formatted_row)

    for object in combined_test_type_objects:
        list_of_combined_test_types.append(object.code)

    for object in all_available_layer_objects:
        list_of_combined_test_layers.append(object.code)

    formatted_rows.append({"IGNORE":"IGNORE", "combined_test_types": list_of_combined_test_types, "combined_test_layers": list_of_combined_test_layers, "layer_id_mapping": map_layers_to_record_return})
    payload = {
        "status": "success",
        "message": "",
        "formatted_results": formatted_rows,
    }
    return JsonResponse(payload, safe=False)


# Paper Tests - Paper Tests
@api_view(['GET', 'POST'])
def FetchCombinedTestEntries(request):
    request_dict = request.POST
    logger.info(message=f"request_dict={request_dict}")

    if request_dict == {}:
        logger.info(message=f"Empty request_dict")
        results = CombinedBoardTest.objects.all()
    else:
        logger.info(message=f"Non-empty request_dict")
        plant_object = Plant.objects.filter(code=request_dict["plant"]).first()
        order_object = Order.objects.filter(plant=plant_object, order_no=request_dict["order_no"]).first()
        results = CombinedBoardTest.objects.filter(plant=plant_object, order=order_object)

    list_of_results = []

    for r in results:
        list_of_results.append({
            "id": r.id,
            "order_no": r.get_order_no(),
            "test_type": r.get_test_type_desc(),
            "test_reason": r.get_test_reason_desc(),
            "test_value": r.test_value,
        })

    logger.info(list_of_results)
    return JsonResponse(list_of_results, safe=False)


# Combined Test Entry - Search Order
@api_view(['GET', 'POST'])
def CombinedSearchOrder(request):
    request_dict = request.POST
    logger.debug(message=f"POST request dict ={request_dict}")
    payload_dict = {}

    for key in request_dict:
        payload_dict[key] = request_dict[key]

    payload_dict["action"] = "search_order"
    logger.debug(message=f"payload_dict={payload_dict}")

    try:
        results = ProgressTableReads(payload=payload_dict)
    except UnexpectedKeyError as e:
        logger.error(message=f"{e}", details="Combined Test Entry - Search Order")
        error = {"Error": "UnexpectedKeyError", "Message": str(e)}
        return JsonResponse(error)
    except UnacceptableActionError as e:
        logger.error(message=f"UnacceptableActionError = {e}", details="Combined Test Entry - Search Order")
        error = {"Error": "UnacceptableActionError", "Message": str(e)}
        return JsonResponse(error)
    except Exception as e:
        logger.error(message=f"Exception = {e}", details="Combined Test Entry - Search Order")
        error = {"Error": "Exception", "Message": str(e)}
        return JsonResponse(error)
    else:
        return JsonResponse(results)

########################################################
# Leaving this here for a reference on how to mass update the database if needed. Hopefully not though.
# I used the urls.py to create an endpoint
# Triggered an app.connect.connect_manager() on page load to trigger the django endpoint
# which executed this function
# See file api/fixtures/csv_files/updated_combined_values.json for how I loaded the variable "updated_values" below
########################################################
# @api_view(['GET', 'POST'])
# def CombinedUpdateRecords(request):
#     for rec in updated_values:
#         if rec["New Value"] != rec["Old Value"]:
#             order = Order.objects.filter(order_no=rec["Order #"]).first()
#             test_type = CombinedBoardTestType.objects.filter(desc=rec["Test Type"]).first()
#             plant = Plant.objects.filter(code="ms").first()
#             if not order:
#                 logger.error(f"No order found {rec['Order #']} | test_type={test_type.code} | old_value={rec['Old Value']} | new_value={rec['New Value']}")
#                 continue
#             if not test_type:
#                 logger.error(f"No test type found {rec['Test Type']}")
#                 continue
#
#             combined_test = CombinedBoardTest.objects.filter(order=order, test_type=test_type, plant=plant).first()
#             logger.info(f"Updating order # {order.order_no} | Test Type {test_type.code} | plant {plant.code} | from_value={rec['Old Value']} to_value={rec['New Value']}")
#             combined_test.test_value = float(rec["New Value"])
#             combined_test.save()
#
#     return JsonResponse({"status": "success"})
