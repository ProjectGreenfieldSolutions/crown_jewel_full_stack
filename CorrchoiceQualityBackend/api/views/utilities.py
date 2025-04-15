from local.globals import MYSQL_ACTIONS, PROGRESS_ACTIONS, TEST_ENTRY_ACTIONS
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from ..services.ProgressTableReads import ProgressTableReads
from ..models.Account import Account
from ..models.Templates import Plant
from ..models.Utility import Vendor, Customer, Corrugator, PaperType, Grade, Litho, Flute, OrderTestCode, \
    SpecialInstructionCode, PaperTestReason, PaperTestType, PaperTestPosition, CombinedBoardTestReason, \
    CombinedBoardTestLayer, CombinedBoardTestType

from ..models.TestEntry import PaperTest, LithoPaperTest, CombinedBoardTest
from ..models.Tracking import Roll, Order, LithoPaper

from copy import deepcopy
import json

from local.Logging import Logger
from local.globals import DEFAULT_PREFERENCES

logger = Logger(__file__)

from CustomExceptions import UnacceptableActionError, UnexpectedKeyError, InvalidTable


def FormatDateForDatabase(ip_date):
    from datetime import datetime
    old_date = datetime.strptime(ip_date, "%m/%d/%y")
    new_date = old_date.strftime("%Y-%m-%d")
    return new_date


class DjangoDataManager:
    def __init__(self):
        logger.info("DjangoDataManager Initialized")
        self.payload = {}
        self.table_objects = {
            # Progress tables
            "order": Order,
            "plant": Plant,
            "vendor": Vendor,
            "customer": Customer,
            "corrugator": Corrugator,
            "grade": Grade,
            "flute": Flute,
            "paper_type": PaperType,
            "order_test_code": OrderTestCode,
            "special_instruction_code": SpecialInstructionCode,
            # Django specific tables
            "account": Account,
            "litho": Litho,
            "paper_test_reason": PaperTestReason,
            "paper_test_type": PaperTestType,
            "paper_test_position": PaperTestPosition,
            "combined_board_test_reason": CombinedBoardTestReason,
            "combined_board_test_layer": CombinedBoardTestLayer,
            "combined_board_test_type": CombinedBoardTestType,
            "paper_test": PaperTest,
            "combined_board_test": CombinedBoardTest,
        }

        self.model_objects = {
            "roll": None,
            "order": None,
            "plant": None,
            "vendor": None,
            "grade": None,
            "customer": None,
            "flute": None,
            "corrugator": None,
            "test_code": None,
            "special_instruction_code": None,
            "paper_test_type": None,
            "paper_test_reason": None,
            "paper_test_position": None,
            "combined_board_test_reason": None,
            "combined_board_test_layer": None,
            "combined_board_test_type": None,
            "author": None,
        }

        self.paper_fields = {
            "roll_no": None,
            "test_reason": None,
            "test_position": None,
            "plant_code": None,
            "author": None,
            "test_entries": None,
        }

        self.number_of_test_entries = 0

        self.roll_results = None
        self.vendor_results = None
        self.grade_results = None
        self.paper_type_results = None

        self.combined_fields = {
            "order_no": None,
            "test_reason": None,
            "author": None,
            "customer_name": None,
            "cust_no": None,
            "flute_code": None,
            "flute_flute_desc": None,
            "corrugator_corru_name": None,
            "corrugator_id": None,
            "test_code": None,
            "special_instruction_code": None,
            "plant_code": None,

            "test_positions": None,
            "test_entries": None,
        }

    @staticmethod
    def MapUsernames(db_records):
        logger.info(message=f"Building results dictionary", details=f"DataManager.MapUsernames")
        results = {}
        for record in db_records:
            results[str(record)] = str(record)
        logger.info(message=f"Returning all results")
        logger.debug(message=f"results={results}")
        return results

    @staticmethod
    def MapDropDowns(db_records):
        logger.info(message=f"Building results dictionary", details=f"DataManager.MapDropDowns")
        results = {}
        for record in db_records:
            results[record.code] = record.get_desc()
        logger.info(message=f"Returning all results")
        logger.debug(message=f"results={results}")
        return results

    @staticmethod
    def MapPaperTests(db_records):
        logger.info(message=f"Building results dictionary", details=f"DataManager.MapPaperTests")
        results = {}
        for index, record in enumerate(db_records):
            results[index] = {
                "roll_no": record.roll.get_roll_no(),
                # TODO - do we need this?
                # "test_type": record.get_test_type_desc(),
                "test_reason": record.get_test_reason_desc(),
                "test_position": record.get_test_position_desc(),
                "average": record.test_value,
            }

        logger.info(message=f"Returning all results")
        logger.debug(message=f"results={results}")
        return results

    @staticmethod
    def MapCombinedTests(db_records):
        logger.info(message=f"Building results dictionary", details=f"DataManager.MapCombinedTests")
        results = {}

        for index, record in enumerate(db_records):
            results[index] = {
                # "roll_no": record.roll.get_roll_no(),
                # "test_reason": record.get_test_reason_desc(),
                # "test_position": record.get_test_position_desc(),
                "value": record.test_value,
            }

        logger.info(message=f"Returning all results")
        logger.debug(message=f"results={results}")
        return results

    @staticmethod
    def GetPlantID(plant_code: str):
        plant_object = Plant.objects.filter(code=plant_code).first()
        logger.debug(f"plant id = {plant_object.id}")
        if plant_object:
            return plant_object
        else:
            raise InvalidTable(f"Unable to locate plant for plant-code={plant_code}")

    def FetchDjangoDatabaseTables(self, plant_code, table_name):
        logger.info(message=f"Running Fetch Django Database Tables")
        logger.info(message=f"params | plant_code={plant_code} | table_name={table_name}")
        table = table_name if table_name[-1] != "s" else table_name[:-1]

        try:
            logger.debug(message=f"seeing if {table} in self.table_objects")
            if table in self.table_objects:
                logger.info(f"Table name matched, fetching from '{table}'")
                table_object = self.table_objects[table]
                logger.info(f"table_object={table_object}")
                plant_obj = self.GetPlantID(plant_code)
                logger.info(f"plant_obj={plant_obj}")

                if table == "account":
                    results = table_object.objects.all().order_by("username")
                elif not table == "plant":
                    if not table == "combined_board_test_layer":
                        results = table_object.objects.exclude(code="null").filter(plant=plant_obj.id).order_by("code")
                    else:
                        results = table_object.objects.exclude(code="null").filter(plant=plant_obj.id)
                else:
                    results = Plant.objects.exclude(code="null").order_by("code")

                if table in TEST_ENTRY_ACTIONS:
                    if "paper" in table:
                        results = self.MapPaperTests(results)
                    elif "combined" in table:
                        results = self.MapCombinedTests(results)
                elif not table == "account":
                    results = self.MapDropDowns(results)
                else:
                    results = self.MapUsernames(results)
            else:
                raise InvalidTable(f"table name provided does not match our records.")
        except InvalidTable as e:
            logger.error(message=f"InvalidTable={e}")
            results = {"Error": e}
        except Exception as e:
            logger.error(message=f"Exception={e}")
            results = {"Error": e}
        else:
            pass

        logger.info(f"results={results}")
        return results

    def FetchProgressRecords(self, plant_code: str, table_name: str, **kwargs):
        # TODO - "find_" + table_name line fails when passing a non-plural table_name (Example: "vendor" failed)
        payload_template = {
            "action": "find_" + table_name if table_name[-1] == "s" else table_name + "s",
            "plant": plant_code,
            "table": table_name if table_name[-1] != "s" else table_name[:-1],
        }

        # Hotfix to change the dynamic creation of action to take
        # This is here to maintain legacy Progress snippet PLUS we only ever fetch a single order
        if payload_template["action"] == "find_orders":
            payload_template["action"] = "search_order"

        try:
            logger.info(kwargs)
            payload_dict = payload_template | kwargs['kwargs']
        except Exception as e:
            payload_dict = deepcopy(payload_template)

        try:
            logger.info(message=f"Running Progress Database Updates | payload_dict={payload_dict}",
                        details=f"FetchProgressRecords")
            results = ProgressTableReads(payload=payload_dict)
        except UnexpectedKeyError as e:
            logger.error(message=f"{e}", details=f"Action = {action}")
            error = {"Error": "UnexpectedKeyError", "Message": str(e)}
            return {"Error": error}
        except UnacceptableActionError as e:
            logger.error(message=f"Exception = {e}", details=f"Action = {action}")
            error = {"Error": "UnacceptableActionError", "Message": str(e)}
            return {"Error": error}
        except Exception as e:
            logger.error(message=f"Exception = {e}", details=f"Action = {action}")
            error = {"Error": "Exception", "Message": str(e)}
            return {"Error": error}
        else:
            logger.debug(message=f"Returning results")
            return results

    def SyncDjangoTables(self, table_name: str, records, plant_code: str):
        logger.debug(message=f"table_name={table_name} | records={records}")
        payload_dict = {
            "table": table_name if table_name[-1] != "s" else table_name[:-1],
        }
        logger.info(message=f"table to access is {payload_dict['table']}")

        if payload_dict['table'] in self.table_objects:
            table_to_update = self.table_objects[payload_dict['table']]
            logger.debug(message=f"records to iterate through | {records}")
            for rec in records:
                logger.debug(f"rec={rec}")
                table_records = table_to_update.objects.filter(code=rec['code']).first()
                logger.debug(message=f"table records={table_records}")

                if not table_records:
                    logger.info(message=f"Adding new record to table {payload_dict['table']}")
                    new_record = table_to_update(code=rec['code'], desc=rec['desc']) if payload_dict[
                                                                                            'table'] == "plant" else table_to_update(
                        code=rec['code'], desc=rec['desc'], plant=self.GetPlantID(plant_code=plant_code))
                    new_record.save()
                else:
                    logger.debug("Record already exists!")

    def ValidateValue(self, table, code):
        logger.info(message=f"Validating {table} for code {code}")
        try:
            if table in ["author"]:
                self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(
                    username=f"{code}").first()
            elif table in ["order"]:
                self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(
                    order_no=f"{code}").first()
            elif table in ["vendor"]:
                # Look for code using Desc
                self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(desc=f"{code}").first()
            else:
                self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(code=f"{code}").first()

        except Exception as e:
            logger.warning(f"Exception={e}", details=f"ValidateValue at start")
            self.model_objects[f"{table}"] = None

        if not self.model_objects[f"{table}"]:
            error = f"Invalid code ({code}) for table {table} was sent in the payload."
            logger.info(message=f"error={error}", details="ValidateValue")
            # if table in ["vendor", "grade", "paper_type", "customer", "flute", "corrugator", "test_code",
            #              "special_instruction_code", "order_test_code"]:
            if table in ["vendor", "grade", "paper_type", "customer", "flute", "corrugator", "test_code",
                         "order_test_code"]:
                logger.info(
                    message=f"Syncing the table ({table}) with ProgressERP database on plant ({self.model_objects['plant'].get_code()})")

                self.SyncDjangoTables(table_name=f"{table}", records=self.FetchProgressRecords(
                    plant_code=self.model_objects['plant'].get_code(), table_name=f"{table}s"),
                                      plant_code=self.model_objects['plant'].get_code())

                try:
                    if table in ["author"]:
                        self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(
                            username=f"{code}").first()
                    elif table in ["order"]:
                        self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(
                            order_no=f"{code}").first()
                    elif table in ["roll"]:
                        self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(
                            roll_no=f"{code}").first()
                    else:
                        self.model_objects[f"{table}"] = self.table_objects[f"{table}"].objects.filter(
                            code=f"{code}").first()
                except Exception as e:
                    message = f"After syncing the ProgressERP databases with Django, still no matching record for {table}.code={code}"
                    logger.error(f"Exception={e} message={message}", details=f"ValidateValue in syncing")
                    raise Exception(f"{message}")
            elif table in ["special_instruction_code"]:
                table_to_update = self.table_objects[table]
                table_record = table_to_update.objects.filter(code=code).first()
                if not table_record:
                    logger.info(message=f"Adding new record to table {table}")
                    new_record = table_to_update(code=code, plant=self.model_objects['plant'])
                    new_record.save()
                else:
                    logger.info("Record already exists!")
            else:
                message = f"Table ({table}) with the code ({code}) is not found!"
                logger.error(message=message)
                raise Exception(f"{message}")
        else:
            logger.info(message=f"{table}.id={self.model_objects[f'{table}'].id}")

    def ValidateRoll(self, roll_no):
        logger.info(message=f"Validating rolls")
        # Validate roll object exists in django database
        self.model_objects['roll'] = Roll.objects.filter(roll_no=roll_no, plant=self.model_objects['plant'].id).first()
        logger.info(self.model_objects['roll'])
        if not self.model_objects['roll']:
            # Doesn't exist in Django database
            logger.info(message=f"Roll not found in system, fetching from Progress and adding to Django")
            results = self.FetchProgressRecords(plant_code=self.model_objects['plant'].get_code(), table_name="rolls",
                                                kwargs={"roll_no": roll_no})
            logger.info("Found roll results")
            logger.info(results)

            # TODO - Ensure single roll return?
            new_roll = Roll()
            new_roll.roll_no = results[0]["roll_no"]
            new_roll.vroll_no = results[0]["vroll_no"]
            new_roll.width = results[0]["actual_width"]
            new_roll.author = self.model_objects["author"]
            new_roll.received_date = FormatDateForDatabase(results[0]["rec_date"])
            new_roll.plant = self.model_objects["plant"]
            new_roll.vendor = self.model_objects["vendor"]
            new_roll.paper_type = self.model_objects["paper_type"]
            new_roll.grade = self.model_objects["grade"]
            new_roll.save()
            self.model_objects['roll'] = Roll.objects.filter(roll_no=roll_no,
                                                             plant=self.model_objects['plant'].id).first()
        else:
            # Exists in Django database
            logger.info(message=f"Roll found in system ({self.model_objects['roll'].get_roll_no()})")

    def ValidateOrder(self, order_no):
        logger.info(message=f"Validating order")

        # Validate order object exists in django database
        self.model_objects['order'] = Order.objects.filter(order_no=order_no,
                                                           plant=self.model_objects['plant'].id).first()

        logger.info(self.model_objects['order'])
        if not self.model_objects['order']:
            # Doesn't exist in Django database
            logger.warning(message=f"Order not found in system, fetching from Progress and adding to Django")
            order_results = self.FetchProgressRecords(plant_code=self.model_objects['plant'].get_code(),
                                                      table_name="orders", kwargs={"order": order_no})
            logger.info("Found order order_results")
            logger.debug(order_results)

            # TODO - Ensure single order return?
            new_order = Order()
            new_order.order_no = order_results["order_no"]
            new_order.cust_po = order_results["cust_po"]
            new_order.ship_no = order_results["ship_no"]
            new_order.order_date = FormatDateForDatabase(order_results["order_date"])
            new_order.ship_date = FormatDateForDatabase(order_results["ship_date"])
            new_order.width = order_results["width"]
            new_order.length = order_results["length"]
            new_order.walls = order_results["number_of_walls"]

            # Foreign Keys
            new_order.plant = self.model_objects["plant"]
            new_order.author = self.model_objects["author"]
            new_order.customer = self.model_objects["customer"]
            new_order.flute = self.model_objects["flute"]
            new_order.corrugator = self.model_objects["corrugator"]
            new_order.test_code = self.model_objects["order_test_code"]
            new_order.spec_code = self.model_objects["special_instruction_code"]
            new_order.save()
            self.model_objects['order'] = Order.objects.filter(order_no=order_no,
                                                               plant=self.model_objects['plant'].id).first()
        else:
            # Exists in Django database
            logger.info(message=f"Order found in system ({self.model_objects['order'].get_order_no()})")

    def UpdateTestEntry(self):
        logger.info(message=f"payload={self.payload}", details="UpdateTestEntry")
        action = self.payload["action"]
        logger.info(message=f"action={action}")

        if action == "paper_test":
            logger.info(message=f"paper test entry detected")
            if self.payload["selected_test_entry"] == "roll_paper":
                logger.info(message=f"roll paper test entry commit start...")
                self.PerformRollPaperTestEntry()
                logger.info(message=f"roll paper test entry commit finished")
            elif self.payload["selected_test_entry"] == "litho_paper":
                logger.info(message=f"litho paper test entry commit start...")
                self.PerformLithoPaperTestEntry()
                logger.info(message=f"litho paper test entry commit finished")

            logger.info(message=f"after test entry ")

            # for field in ["roll_no", "plant_code", "author", "test_reason", "test_position", "vendor", "paper_type",
            #               "grade"]:
            #     self.paper_fields[field] = payload[field]
            #
            # self.paper_fields["test_entries"] = json.loads(payload["test_entries"])
            #
            # tables = ["plant", "author", "vendor", "paper_type", "grade"]
            # codes = [self.paper_fields["plant_code"], self.paper_fields["author"], self.paper_fields["vendor"],
            #          self.paper_fields["paper_type"], self.paper_fields["grade"]]
            # for table, code in zip(tables, codes):
            #     self.ValidateValue(table=table, code=code)
            #
            # self.ValidateRoll(roll_no=self.paper_fields["roll_no"])
            #

        elif action == "combined_board_test":
            logger.info(message=f"combined board entry detected")
            self.PerformCombinedBoardTestEntry()
            logger.info(message=f"after test entry ")

            # for field in ["order_no", "plant_code", "author", "test_reason", "customer_name", "cust_no", "flute_code",
            #               "flute_flute_desc", "corrugator_corru_name", "corru_id", "test_code",
            #               "special_instruction_code"]:
            #     logger.info(f"field={field} value={payload[field]}")
            #     self.combined_fields[field] = payload[field]
            #
            # for number in range(1, 8):
            #     self.combined_fields[f"layer_value_{number}"] = payload[f"layer_value_{number}"]
            #     self.combined_fields[f"layer_position_{number}"] = payload[f"layer_position_{number}"]
            #
            # self.combined_fields["test_entries"] = json.loads(payload["test_entries"])
            #
            # tables = ["plant", "author",
            #           "customer", "flute",
            #           "corrugator", "order_test_code",
            #           "special_instruction_code"]
            #
            # codes = [self.combined_fields["plant_code"], self.combined_fields["author"],
            #          self.combined_fields["cust_no"], self.combined_fields["flute_code"],
            #          self.combined_fields["corru_id"], self.combined_fields["test_code"],
            #          self.combined_fields["special_instruction_code"]]
            #
            # for table, code in zip(tables, codes):
            #     self.ValidateValue(table=table, code=code)
            #
            # self.ValidateOrder(order_no=self.combined_fields["order_no"])
            #
            # self.PerformCombinedBoardTestEntry()

    def PerformRollPaperTestEntry(self):
        logger.info(message=f"self.payload={self.payload}")

        # Variables for Roll Paper Test Entries
        roll_no = self.payload["roll_no"]
        roll_data = None

        # Variables to determine if we're updating an existing record
        target_id = None
        updated_test_value = None
        updated_test_type = None
        updated_test_reason = None
        updated_test_position = None

        try:
            target_id = self.payload["id"]
            updated_test_value = self.payload["test_value"]
            updated_test_type = PaperTestType.objects.filter(code=self.payload["test_type"]).first()
            updated_test_reason = PaperTestReason.objects.filter(code=self.payload["test_reason"]).first()
            updated_test_position = PaperTestPosition.objects.filter(code=self.payload["test_position"]).first()
        except:
            target_id = None

        if target_id:
            updated_test = PaperTest.objects.filter(id=target_id).first()
            updated_test.test_value = updated_test_value
            updated_test.test_type = updated_test_type
            updated_test.test_reason = updated_test_reason
            updated_test.test_position = updated_test_position
            updated_test.save()
            return

        # Variables for both types of paper test entries
        username = self.payload["author"]
        plant_code = self.payload["plant_code"]
        test_reason = self.payload["test_reason"]
        test_position = self.payload["test_position"]
        test_entries = self.payload["test_entries"]

        #####################################################################
        # Account/Author Related Tables
        #####################################################################
        if not Account.objects.filter(username=username).exists():
            a = Account.objects.create_user(username=username, password="NULL")
            a.home_plant = plant_code
            a.preferences = DEFAULT_PREFERENCES
            logger.info("save author")
            a.save()

        account_obj = Account.objects.filter(username=username).first()

        plant_obj = Plant.objects.filter(code=plant_code).first()
        #####################################################################
        # Roll Related Tables
        #####################################################################
        if not Roll.objects.filter(roll_no=roll_no, plant=plant_obj).exists():
            roll_data = ProgressTableReads(
                payload={"action": "find_rolls", "plant": plant_code, "roll_no": roll_no}
            )[0]
            logger.debug(f"roll_data={roll_data}")

            logger.debug(f"Vendor")
            if not Vendor.objects.filter(code=roll_data["vendor_code"].lower(), desc=roll_data["vendor_name"],
                                         plant=plant_obj).exists():
                v = Vendor(code=roll_data["vendor_code"].lower(), desc=roll_data["vendor_name"],
                           plant=plant_obj)
                logger.info("save vendor")
                v.save()

            logger.debug(f"PaperType")
            if not PaperType.objects.filter(code=roll_data["inv_tcode"].lower(), plant=plant_obj).exists():
                p = PaperType(code=roll_data["inv_tcode"].lower(), plant=plant_obj)
                logger.info("save papertype")
                p.save()

            logger.debug(f"Grade")
            if not Grade.objects.filter(code=roll_data["grade"].lower(), plant=plant_obj).exists():
                g = Grade(code=roll_data["grade"].lower(), plant=plant_obj)
                logger.info("save grade")
                g.save()

            vendor_obj = Vendor.objects.filter(code=roll_data["vendor_code"], plant=plant_obj).first()
            paper_type_obj = PaperType.objects.filter(code=roll_data["inv_tcode"],
                                                      plant=plant_obj).first()
            grade_obj = Grade.objects.filter(code=roll_data["grade"], plant=plant_obj).first()

            logger.debug(f"Roll")
            r = Roll(roll_no=roll_data["roll_no"], vroll_no=roll_data["vroll_no"],
                     tally_id=roll_data["talley_id"].strip(),
                     width=roll_data["actual_width"], received_date=FormatDateForDatabase(roll_data["rec_date"]),
                     weight=roll_data["orig_weight"],
                     linear_foot=roll_data["orig_linear_f"], msf=roll_data["orig_msf"],
                     cost_by_ton=roll_data["cost_by_ton"], cost_by_msf=roll_data["cost_by_msf"],
                     mill=roll_data["mill"], moisture=roll_data["moisture"],
                     vendor=vendor_obj, paper_type=paper_type_obj, grade=grade_obj,
                     plant=plant_obj)

            logger.info("saving roll")
            r.save()

        #####################################################################
        # Test Entry Related Tables
        #####################################################################
        if not PaperTestReason.objects.filter(code=test_reason, plant=plant_obj).exists:
            p = PaperTestReason(code=test_reason, desc=test_reason, plant=plant_obj)
            logger.info("saving paper_test_reason")
            p.save()

        if not PaperTestPosition.objects.filter(code=test_position, plant=plant_obj).exists:
            p = PaperTestPosition(code=test_position, desc=test_position,
                                  plant=plant_obj)
            logger.info("saving paper_test_position")
            p.save()

        roll_obj = Roll.objects.filter(roll_no=roll_no, plant=plant_obj).first()
        paper_test_reason_obj = PaperTestReason.objects.filter(code=test_reason, plant=plant_obj).first()
        paper_test_position_obj = PaperTestPosition.objects.filter(code=test_position, plant=plant_obj).first()

        if not roll_data:
            roll_data = ProgressTableReads(
                payload={"action": "find_rolls", "plant": plant_code, "roll_no": roll_no}
            )[0]
        """
        update_selected_panel row={'talley_id': '409615-244A01181', 'roll_no': '456456MS', 'vroll_no': '159853J18M', 'vendor_code': 'Greif-Ma', 'vendor_name': 'Greif-Massillon', 'rec_date': '09/15/18', 'grade': '23', 'inv_tcode': 'M', 'actual_width': '39.875', 'orig_weight': '2641', 'orig_linear_f': '34300', 'orig_msf': '113.976', 'cost_by_ton': '590', 'cost_by_msf': '6.785', 'mill': '', 'moisture': '7.4', 'inv_pcode': 'MS'}
            """

        test_entries = json.loads(test_entries)
        for test_entry_no in test_entries:
            value = test_entries[test_entry_no]["value"]
            test_type = test_entries[test_entry_no]["type"]

            if not PaperTestType.objects.filter(code=test_type, plant=plant_obj).exists():
                p = PaperTestType(code=test_type.lower().replace(" ", "_"), desc=test_type,
                                  plant=plant_obj)
                logger.info("saving paper_test_type")
                p.save()

            paper_test_type_obj = PaperTestType.objects.filter(code=test_type, plant=plant_obj).first()

            if target_id:
                updated_test = PaperTest.objects.filter(id=target_id).first()
                updated_test.test_value = value
                updated_test.test_type = paper_test_type_obj
                updated_test.test_reason = paper_test_reason_obj
                updated_test.test_position = paper_test_position_obj
                updated_test.save()
            else:
                new_test = PaperTest(test_value=value, roll=roll_obj, author=account_obj,
                                     test_type=paper_test_type_obj, test_reason=paper_test_reason_obj,
                                     test_position=paper_test_position_obj, plant=plant_obj)
                new_test.save()

    def PerformLithoPaperTestEntry(self):
        logger.info(message=f"self.payload={self.payload}")

        ##############################################################
        # Code to update the records
        ##############################################################
        litho_uuid = self.payload["litho_uuid"]
        litho_pt = self.payload["litho_pt"]

        # Variables to determine if we're updating an existing record
        target_id = None
        updated_test_value = None
        updated_test_type = None
        updated_test_reason = None
        updated_test_position = None
        updated_litho_point = None

        try:
            target_id = self.payload["id"]
        except:
            target_id = None

        if target_id:
            # Update the Litho Paper table, if necessary
            try:
                # Access the litho paper object
                updated_litho_paper = LithoPaper.objects.filter(litho_uuid=self.payload["litho_uuid"]).first()

                # Assign updated litho point value
                updated_litho_paper.litho_pt = self.payload["litho_pt"]

                logger.info("Saving the updated litho paper object")
                updated_litho_paper.save()
            except:
                logger.info(f"No litho pt/litho uuid value(s) provided | litho_pt={litho_pt} litho_uuid={litho_uuid}")

            try:
                updated_test_value = self.payload["test_value"]
                updated_test_type = PaperTestType.objects.filter(code=self.payload["test_type"]).first()
                updated_test_reason = PaperTestReason.objects.filter(code=self.payload["test_reason"]).first()
                updated_test_position = PaperTestPosition.objects.filter(code=self.payload["test_position"]).first()
            except:
                logger.error("Something broken in the update litho paper test entry try-catch")
                return

            # Updated the Litho Paper Test Entry table
            updated_test = LithoPaperTest.objects.filter(id=target_id).first()
            updated_test.test_value = updated_test_value
            updated_test.test_type = updated_test_type
            updated_test.test_reason = updated_test_reason
            updated_test.test_position = updated_test_position
            updated_test.save()
            return

        # Variables for both types of paper test entries
        username = self.payload["author"]
        plant_code = self.payload["plant_code"]
        test_reason = self.payload["test_reason"]
        test_position = self.payload["test_position"]
        test_entries = self.payload["test_entries"]

        # Insurance policy to determine if we have the necessary payloads for this
        try:
            target_id = self.payload["id"]
        except:
            logger.info("Updated payload keys not appropriately assigned, continuing with normal new commits")
            logger.info(f"target_id={target_id} updated_test_value={updated_test_value} updated_test_type={updated_test_type} updated_test_reason={updated_test_reason}")
            target_id = None

        if target_id:
            # Update with the provided values
            updated_test = CombinedBoardTest.objects.filter(id=target_id).first()
            updated_test.test_value = updated_test_value
            updated_test.test_type = updated_test_type
            updated_test.test_reason = updated_test_reason
            # Commit the new change to the database

            # Note: its okay to avoid doing any of the below table creations as we're only allowing the user to make
            #       Test Value change OR drop-down selections. Drop downs all already exist so no need to execute
            #       the below logic
            updated_test.save()
            return

        #####################################################################
        # Account/Author Related Tables
        #####################################################################
        if not Account.objects.filter(username=username).exists():
            logger.info("creating author")
            a = Account.objects.create_user(username=username, password="NULL")
            a.home_plant = plant_code
            a.preferences = DEFAULT_PREFERENCES
            logger.info("save author")
            a.save()

        account_obj = Account.objects.filter(username=username).first()
        plant_obj = Plant.objects.filter(code=plant_code).first()

        #####################################################################
        # Litho Paper Related Table
        #####################################################################
        if not LithoPaper.objects.filter(litho_uuid=litho_uuid, plant=plant_obj).exists():
            logger.info("creating litho_paper_object")
            litho_paper = LithoPaper(litho_uuid=litho_uuid, litho_pt=litho_pt, plant=plant_obj)
            logger.info("saving litho_paper_object")
            litho_paper.save()

        if not LithoPaper.objects.filter(litho_uuid=litho_uuid, litho_pt=litho_pt, plant=plant_obj).first():
            logger.info("Updating the litho point value")
            litho_paper = LithoPaper.objects.filter(litho_uuid=litho_uuid, plant=plant_obj).first()
            litho_paper.litho_pt = litho_pt
            logger.info(f"saving litho_paper_object with value point of '{litho_paper.litho_pt}'")
            litho_paper.save()

        #####################################################################
        # Test Entry Related Tables
        #####################################################################
        if not PaperTestReason.objects.filter(code=test_reason, plant=plant_obj).exists():
            p = PaperTestReason(code=test_reason, desc=test_reason, plant=plant_obj)
            logger.info("saving paper_test_reason")
            p.save()

        if not PaperTestPosition.objects.filter(code=test_position, plant=plant_obj).exists():
            p = PaperTestPosition(code=test_position, desc=test_position,
                                  plant=plant_obj)
            logger.info("saving paper_test_position")
            p.save()

        paper_test_reason_obj = PaperTestReason.objects.filter(code=test_reason, plant=plant_obj).first()
        paper_test_position_obj = PaperTestPosition.objects.filter(code=test_position, plant=plant_obj).first()

        litho_paper_obj = LithoPaper.objects.filter(litho_uuid=litho_uuid, plant=plant_obj).first()

        # Test Entry Values
        test_entries = json.loads(test_entries)

        for test_entry_no in test_entries:
            value = test_entries[test_entry_no]["value"]
            # If the value is zero, do not enter this into the database
            if float(value) == 0.0:
                continue
            test_type = test_entries[test_entry_no]["type"]

            if not PaperTestType.objects.filter(code=test_type, plant=plant_obj).exists():
                p = PaperTestType(code=test_type.lower().replace(" ", "_"), desc=test_type,
                                  plant=plant_obj)
                logger.info("saving paper_test_type")
                p.save()

            paper_test_type_obj = PaperTestType.objects.filter(code=test_type, plant=plant_obj).first()

            # Uncomment for verification that all the related table objects are found
            # logger.info(value)
            # logger.info(litho_paper_obj.id)
            # logger.info(account_obj.id)
            # logger.info(paper_test_type_obj.id)
            # logger.info(paper_test_reason_obj.id)
            # logger.info(paper_test_position_obj.id)
            # logger.info(plant_obj.id)

            new_test = LithoPaperTest(test_value=value, litho_paper=litho_paper_obj, author=account_obj,
                                      test_type=paper_test_type_obj, test_reason=paper_test_reason_obj,
                                      test_position=paper_test_position_obj, plant=plant_obj)
            logger.info("saving litho paper test to system")
            new_test.save()

    def PerformCombinedBoardTestEntry(self):
        logger.debug("Performing combined board test entry function")

        ##############################################################
        # Code to update the records
        ##############################################################
        # Variables to determine if we're updating an existing record
        target_id = None
        updated_test_value = None
        updated_test_type = None
        updated_test_reason = None

        # Insurance policy to determine if we have the necessary payloads for this
        try:
            target_id = self.payload["id"]
            updated_test_value = self.payload["test_value"]
            updated_test_type = CombinedBoardTestType.objects.filter(code=self.payload["test_type"]).first()
            updated_test_reason = CombinedBoardTestReason.objects.filter(code=self.payload["test_reason"]).first()
        except:
            logger.info("Updated payload keys not appropriately assigned, continuing with normal new commits")
            logger.info(f"target_id={target_id} updated_test_value={updated_test_value} updated_test_type={updated_test_type} updated_test_reason={updated_test_reason}")
            target_id = None

        if target_id:
            # Update with the provided values
            updated_test = CombinedBoardTest.objects.filter(id=target_id).first()
            updated_test.test_value = updated_test_value
            updated_test.test_type = updated_test_type
            updated_test.test_reason = updated_test_reason
            # Commit the new change to the database

            # Note: its okay to avoid doing any of the below table creations as we're only allowing the user to make
            #       Test Value change OR drop-down selections. Drop downs all already exist so no need to execute
            #       the below logic
            updated_test.save()
            return

        # Values used throughout each test entry
        username = self.payload["author"]
        order_no = self.payload["order_no"]
        plant_code = self.payload["plant_code"]
        test_reason = self.payload["test_reason"]
        spec_code = self.payload["special_instruction_code"]
        layer_1 = self.payload["layer_position_1"]
        layer_2 = self.payload["layer_position_2"]
        layer_3 = self.payload["layer_position_3"]
        layer_4 = self.payload["layer_position_4"]
        layer_5 = self.payload["layer_position_5"]
        layer_6 = self.payload["layer_position_6"]
        layer_7 = self.payload["layer_position_7"]
        roll_1 = self.payload["layer_value_1"]
        roll_2 = self.payload["layer_value_2"]
        roll_3 = self.payload["layer_value_3"]
        roll_4 = self.payload["layer_value_4"]
        roll_5 = self.payload["layer_value_5"]
        roll_6 = self.payload["layer_value_6"]
        roll_7 = self.payload["layer_value_7"]

        #####################################################################
        # Account/Author Related Tables
        #####################################################################
        if not Account.objects.filter(username=username).exists():
            a = Account.objects.create_user(username=username, password="NULL")
            a.home_plant = plant_code
            a.preferences = DEFAULT_PREFERENCES
            logger.info("save author")
            a.save()

        account_obj = Account.objects.filter(username=username).first()

        plant_obj = Plant.objects.filter(code=plant_code).first()

        #####################################################################
        # Roll Related Tables
        #####################################################################
        logger.debug("Roll related tables")
        # Ensure that the layer / value table records exist
        number_of_entries = 8
        for n in range(1, number_of_entries):
            logger.debug(f"entry number {n}")
            roll_no = self.payload["layer_value_" + str(n)]
            test_layer = self.payload["layer_position_" + str(n)]
            ###########################
            # Combined Board Test Layer
            ###########################
            logger.debug("Conditional: test_layer != ''")
            if not test_layer == "":
                if not CombinedBoardTestLayer.objects.filter(code=test_layer.lower().replace(" ", "_"),
                                                             plant=plant_obj).exists():
                    c = CombinedBoardTestLayer(code=test_layer.lower().replace(" ", "_"), desc=test_layer,
                                               plant=plant_obj)
                    logger.info("save test_layer")
                    c.save()

            logger.debug("Conditional: roll_no != ''")
            if not roll_no == "":
                # Copied the below function over to method "RollVerification"; needed the roll creation logic
                if Roll.objects.filter(roll_no=roll_no, plant=plant_obj).exists():
                    logger.debug(f"roll exists {roll_no}")
                    continue

                logger.debug(f"spec code={spec_code}")
                if not spec_code.upper() == "LL":
                    logger.debug(f"spec code ({spec_code}) NOT LL")
                    # Note: roll_1 is the litho.code table field
                    litho_obj = Litho.objects.filter(code=roll_1, plant=plant_obj).first()
                    if litho_obj:
                        raise Exception(
                            f"Failure - Attempting to assign Litho to a non 'LL' spec_code (spec_code={spec_code})")
                    roll_data = ProgressTableReads(
                        payload={"action": "find_rolls", "plant": plant_code, "roll_no": roll_no}
                    )[0]

                    if not Vendor.objects.filter(code=roll_data["vendor_code"], desc=roll_data["vendor_name"],
                                                 plant=plant_obj).exists():
                        v = Vendor(code=roll_data["vendor_code"], desc=roll_data["vendor_name"], plant=plant_obj)
                        logger.info("save vendor")
                        v.save()

                    if not PaperType.objects.filter(code=roll_data["inv_tcode"], plant=plant_obj).exists():
                        p = PaperType(code=roll_data["inv_tcode"], plant=plant_obj)
                        logger.info("save papertype")
                        p.save()

                    if not Grade.objects.filter(code=roll_data["grade"], plant=plant_obj).exists():
                        g = Grade(code=roll_data["grade"], plant=plant_obj)
                        logger.info("save grade")
                        g.save()

                    vendor_obj = Vendor.objects.filter(code=roll_data["vendor_code"], plant=plant_obj).first()
                    paper_type_obj = PaperType.objects.filter(code=roll_data["inv_tcode"],
                                                              plant=plant_obj).first()
                    grade_obj = Grade.objects.filter(code=roll_data["grade"], plant=plant_obj).first()

                    ###########################
                    # Roll
                    ###########################
                    if not Roll.objects.filter(roll_no=roll_data["roll_no"], plant=plant_obj).exists():
                        r = Roll(roll_no=roll_data["roll_no"], vroll_no=roll_data["vroll_no"],
                                 tally_id=roll_data["talley_id"].strip(),
                                 width=roll_data["actual_width"],
                                 received_date=FormatDateForDatabase(roll_data["rec_date"]),
                                 weight=roll_data["orig_weight"],
                                 linear_foot=roll_data["orig_linear_f"], msf=roll_data["orig_msf"],
                                 cost_by_ton=roll_data["cost_by_ton"], cost_by_msf=roll_data["cost_by_msf"],
                                 mill=roll_data["mill"], moisture=roll_data["moisture"],
                                 vendor=vendor_obj, paper_type=paper_type_obj, grade=grade_obj,
                                 plant=plant_obj)
                        logger.info("save roll")
                        r.save()

        #####################################################################
        # Order Related Tables
        #####################################################################
        logger.debug("Order related tables")
        order_data = ProgressTableReads(
            payload={"action": "search_order", "plant": plant_code, "order": order_no})

        if not Customer.objects.filter(code=order_data["cust_no"], plant=plant_obj).exists():
            c = Customer(code=order_data["cust_no"], desc=order_data["customer_name"], plant=plant_obj)
            logger.info("save customer")
            c.save()

        if not Flute.objects.filter(code=order_data["flute_code"], desc=order_data["flute_flute_desc"],
                                    plant=plant_obj).exists():
            f = Flute(code=order_data["flute_code"], desc=order_data["flute_flute_desc"], plant=plant_obj)
            logger.info("save flute")
            f.save()

        if not Corrugator.objects.filter(desc=order_data["corrugator_corru_name"], plant=plant_obj).exists():
            c = Corrugator(code=order_data["corru_id"], desc=order_data["corrugator_corru_name"],
                           plant=plant_obj)
            logger.info("save corrugator")
            c.save()

        if not OrderTestCode.objects.filter(code=order_data["test_code"], plant=plant_obj).exists():
            o = OrderTestCode(code=order_data["test_code"], plant=plant_obj)
            logger.info("save order")
            o.save()

        if not SpecialInstructionCode.objects.filter(code=order_data["spec_code"], plant=plant_obj).exists():
            s = SpecialInstructionCode(code=order_data["spec_code"], plant=plant_obj)
            logger.info("save special_instruction_code")
            s.save()

        #####################################################################
        # Acquire Objects For Order Table
        #####################################################################
        logger.debug("Acquire objects for order table")
        customer_obj = Customer.objects.filter(desc=order_data["customer_name"], plant=plant_obj).first()
        flute_obj = Flute.objects.filter(desc=order_data["flute_flute_desc"], plant=plant_obj).first()
        corrugator_obj = Corrugator.objects.filter(desc=order_data["corrugator_corru_name"],
                                                   plant=plant_obj).first()
        order_test_code_obj = OrderTestCode.objects.filter(code=order_data["test_code"],
                                                           plant=plant_obj).first()
        special_instruction_code_obj = SpecialInstructionCode.objects.filter(code=order_data["spec_code"],
                                                                             plant=plant_obj).first()

        #####################################################################
        # Depends on customer, flute, corrugator, test_code, special_instruction_code
        #####################################################################
        if not Order.objects.filter(order_no=order_data["order_no"], plant=plant_obj).exists():
            o = Order(order_no=order_data["order_no"], order_date=FormatDateForDatabase(order_data["order_date"]),
                      cust_po=order_data["cust_po"], ship_no=order_data["ship_no"],
                      ship_date=FormatDateForDatabase(order_data["ship_date"]), width=order_data["width"],
                      length=order_data["length"],
                      walls=order_data["number_of_walls"], customer=customer_obj, flute=flute_obj,
                      corrugator=corrugator_obj, test_code=order_test_code_obj,
                      spec_code=special_instruction_code_obj, plant=plant_obj)
            logger.info("save order")
            o.save()

        order_obj = Order.objects.filter(order_no=order_data["order_no"], plant=plant_obj).first()

        #####################################################################
        # Combined Board Test Entry Related Tables
        #####################################################################
        if not CombinedBoardTestReason.objects.filter(code=test_reason.lower().replace(" ", "_"),
                                                      plant=plant_obj).exists():
            c = CombinedBoardTestReason(code=test_reason.lower().replace(" ", "_"), desc=test_reason,
                                        plant=plant_obj)
            logger.info("save combined board test reason")
            c.save()

        test_reason_obj = CombinedBoardTestReason.objects.filter(code=test_reason.lower().replace(" ", "_"),
                                                                 plant=plant_obj).first()

        test_layer_1_obj = None
        roll_1_obj = None
        litho_obj = None
        test_layer_2_obj = None
        roll_2_obj = None
        test_layer_3_obj = None
        roll_3_obj = None
        test_layer_4_obj = None
        roll_4_obj = None
        test_layer_5_obj = None
        roll_5_obj = None
        test_layer_6_obj = None
        roll_6_obj = None
        test_layer_7_obj = None
        roll_7_obj = None

        if not layer_1 == "" and not roll_1 == "":
            test_layer_1_obj = CombinedBoardTestLayer.objects.filter(code=layer_1.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            if special_instruction_code_obj.code.upper() != "LL":
                roll_1_obj = Roll.objects.filter(roll_no=roll_1, plant=plant_obj).first()
            else:
                litho_obj = Litho.objects.filter(code=roll_1.lower(), plant=plant_obj).first()

        if not layer_2 == "" and not roll_2 == "":
            test_layer_2_obj = CombinedBoardTestLayer.objects.filter(code=layer_2.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            roll_2_obj = Roll.objects.filter(roll_no=roll_2, plant=plant_obj).first()

        if not layer_3 == "" and not roll_3 == "":
            test_layer_3_obj = CombinedBoardTestLayer.objects.filter(code=layer_3.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            roll_3_obj = Roll.objects.filter(roll_no=roll_3, plant=plant_obj).first()

        if not layer_4 == "" and not roll_4 == "":
            test_layer_4_obj = CombinedBoardTestLayer.objects.filter(code=layer_4.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            roll_4_obj = Roll.objects.filter(roll_no=roll_4, plant=plant_obj).first()

        if not layer_5 == "" and not roll_5 == "":
            test_layer_5_obj = CombinedBoardTestLayer.objects.filter(code=layer_5.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            roll_5_obj = Roll.objects.filter(roll_no=roll_5, plant=plant_obj).first()

        if not layer_6 == "" and not roll_6 == "":
            test_layer_6_obj = CombinedBoardTestLayer.objects.filter(code=layer_6.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            roll_6_obj = Roll.objects.filter(roll_no=roll_6, plant=plant_obj).first()

        if not layer_7 == "" and not roll_7 == "":
            test_layer_7_obj = CombinedBoardTestLayer.objects.filter(code=layer_7.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
            roll_7_obj = Roll.objects.filter(roll_no=roll_7, plant=plant_obj).first()

        #####################################################################
        # Commit Test Entries To Database
        #####################################################################

        logger.debug("Committing test entries to database")
        # Test entries
        test_entries = json.loads(self.payload["test_entries"])
        for test_entry, keyvalue in test_entries.items():
            test_value = keyvalue["value"]
            test_type = keyvalue["type"]
            if not test_value == 0.0 and not test_value == "":
                if not CombinedBoardTestType.objects.filter(code=test_type.lower().replace(" ", "_"),
                                                            plant=plant_obj).exists():
                    c = CombinedBoardTestType(code=test_type.lower().replace(" ", "_"), desc=test_type,
                                              plant=plant_obj)
                    logger.info("save combined board test type")
                    c.save()

                test_type_obj = CombinedBoardTestType.objects.filter(code=test_type.lower().replace(" ", "_"),
                                                                     plant=plant_obj).first()
                logger.info(test_type_obj.code)
                new_test = CombinedBoardTest(
                    test_value=test_value, order=order_obj, author=account_obj, test_reason=test_reason_obj,
                    test_type=test_type_obj, plant=plant_obj,
                    test_layer_1=test_layer_1_obj, test_layer_2=test_layer_2_obj, test_layer_3=test_layer_3_obj,
                    test_layer_4=test_layer_4_obj, test_layer_5=test_layer_5_obj, test_layer_6=test_layer_6_obj,
                    test_layer_7=test_layer_7_obj, test_litho_1=litho_obj, test_roll_1=roll_1_obj,
                    test_roll_2=roll_2_obj,
                    test_roll_3=roll_3_obj, test_roll_4=roll_4_obj, test_roll_5=roll_5_obj, test_roll_6=roll_6_obj,
                    test_roll_7=roll_7_obj)
                logger.info("saving combined test entry")
                new_test.save()

    # def PerformCombinedBoardTestEntry(self):
    #     logger.info("In combined test entry")
    #     logger.info(self.combined_fields["test_entries"])
    #     self.model_objects["combined_board_test_reason"] = CombinedBoardTestReason.objects.filter(
    #         code=self.combined_fields["test_reason"]).first()
    #
    #     logger.info(self.combined_fields["test_entries"].items())
    #     for index, keyvalue in self.combined_fields["test_entries"].items():
    #         logger.info(keyvalue)
    #
    #         # Skip the record creation if the value is 0
    #         if float(keyvalue["value"]) == 0.0:
    #             continue
    #
    #         logger.info("Begin new test entry")
    #         self.model_objects["combined_board_test_type"] = CombinedBoardTestType.objects.filter(
    #             code=keyvalue["type"]).first()
    #
    #         new_test_entry = CombinedBoardTest()
    #         new_test_entry.test_value = keyvalue["value"]
    #         new_test_entry.order = self.model_objects["order"]
    #         new_test_entry.plant = self.model_objects["plant"]
    #         new_test_entry.author = self.model_objects["author"]
    #         new_test_entry.test_type = self.model_objects["combined_board_test_type"]
    #         new_test_entry.test_reason = self.model_objects["combined_board_test_reason"]
    #
    #         if self.combined_fields["special_instruction_code"] == "LL":
    #             new_test_entry.test_litho_1 = Litho.objects.filter(
    #                 code=self.combined_fields["layer_value_1"]).first()
    #         else:
    #             new_test_entry.test_roll_1 = Roll.objects.filter(
    #                 roll_no=self.combined_fields["layer_value_1"]).first()
    #
    #         new_test_entry.test_roll_2 = Roll.objects.filter(roll_no=self.combined_fields["layer_value_2"]).first()
    #         new_test_entry.test_roll_3 = Roll.objects.filter(roll_no=self.combined_fields["layer_value_3"]).first()
    #         new_test_entry.test_roll_4 = Roll.objects.filter(roll_no=self.combined_fields["layer_value_4"]).first()
    #         new_test_entry.test_roll_5 = Roll.objects.filter(roll_no=self.combined_fields["layer_value_5"]).first()
    #         new_test_entry.test_roll_6 = Roll.objects.filter(roll_no=self.combined_fields["layer_value_6"]).first()
    #         new_test_entry.test_roll_7 = Roll.objects.filter(roll_no=self.combined_fields["layer_value_7"]).first()
    #         new_test_entry.test_layer_1 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_1"]).first()
    #         new_test_entry.test_layer_2 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_2"]).first()
    #         new_test_entry.test_layer_3 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_3"]).first()
    #         new_test_entry.test_layer_4 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_4"]).first()
    #         new_test_entry.test_layer_5 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_5"]).first()
    #         new_test_entry.test_layer_6 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_6"]).first()
    #         new_test_entry.test_layer_7 = CombinedBoardTestLayer.objects.filter(
    #             code=self.combined_fields["layer_position_7"]).first()
    #         try:
    #             new_test_entry.save()
    #         except Exception as e:
    #             logger.error(e)

    def DeleteTest(self, payload):
        logger.info(message=f"payload={payload}", details="DeleteTest")
        action = payload["action"]
        try:
            test_entry_type = payload["test_entry_type"]
        except:
            logger.info(f"No special test entry type found (roll_paper or litho_paper)")
            test_entry_type = None

        logger.info(message=f"action={action}")

        if action == "paper_test":
            logger.info(message=f"paper test deletion detected")
            if test_entry_type == "roll_paper":
                record_object = PaperTest.objects.filter(id=payload["id"])
            elif test_entry_type == "litho_paper":
                record_object = LithoPaperTest.objects.filter(id=payload["id"])
            else:
                message = f"test entry type should of been something"
                logger.error(message=message)
                raise Exception(message)

            if not record_object:
                message = f"Record with id={payload['id']} doesn't exist"
                logger.warning(message=message)
                raise Exception(message)
            else:
                record_object.delete()
                logger.info(message=f"Deleted")

        elif action == "combined_board_test":
            logger.info(message=f"combined board test deletion detected")
            record_object = CombinedBoardTest.objects.filter(id=payload["id"])
            if not record_object:
                message = f"Record with id={payload['id']} doesn't exist"
                logger.warning(message=message)
                raise Exception(message)
            else:
                record_object.delete()
                logger.info(message=f"Deleted")


@api_view(['GET', 'POST'])
def UtilityData(request):
    sync_flag = False
    payload_dict = request.POST
    action = payload_dict['action']
    logger.info(message=f"action={action}", details=f"UtilityData")
    try:
        sync_flag = payload_dict['update']
    except Exception as e:
        logger.debug(message=f"syncing flag not detected... {e}")
        sync_flag = False
    else:
        if payload_dict['update']:
            sync_flag = True

    if action in PROGRESS_ACTIONS:
        logger.debug(message=f"Executing Progress Connection", details="UtilityData")
        try:
            results = ProgressTableReads(payload=payload_dict)
        except UnexpectedKeyError as e:
            logger.error(message=f"{e}", details=f"Action = {action}")
            error = {"Error": "UnexpectedKeyError", "Message": str(e)}
            return JsonResponse(error)
        except UnacceptableActionError as e:
            logger.error(message=f"Exception = {e}", details=f"Action = {action}")
            error = {"Error": "UnacceptableActionError", "Message": str(e)}
            return JsonResponse(error)
        except Exception as e:
            logger.error(message=f"Exception = {e}", details=f"Action = {action}")
            error = {"Error": "Exception", "Message": str(e)}
            return JsonResponse(error)
        else:
            return JsonResponse(results)
    elif action in MYSQL_ACTIONS:
        logger.debug(
            message=f"Executing MYSQL_ACTIONS | plant_code={payload_dict['plant_code']} | table_name={payload_dict['action']}")

        data_manager = DjangoDataManager()

        if sync_flag:
            logger.debug(f"action={payload_dict['action']}")
            try:
                data_manager.SyncDjangoTables(table_name=payload_dict["action"],
                                              records=data_manager.FetchProgressRecords(
                                                  plant_code=payload_dict["plant_code"],
                                                  table_name=payload_dict["action"]),
                                              plant_code=payload_dict['plant_code'])
            except Exception as e:
                logger.warning(message=f"SyncDjangoTables code didn't execute ({e})")
            else:
                logger.debug(message=f"Django tables updated")

        results = data_manager.FetchDjangoDatabaseTables(plant_code=payload_dict["plant_code"],
                                                         table_name=payload_dict["action"])

        if results:
            logger.debug(message=f"results is true", details="if results")
            logger.debug(message=f"results={results}", details="if results")
        else:
            logger.warning(message=f"No results found for payload_dict['action']={payload_dict['action']}",
                           details="MYSQL_ACTIONS")

        return JsonResponse(results, safe=False)
    else:
        error = {'error': "invalid action passed (See MYSQL_ACTIONS or PROGRESS_ACTIONS"}
        return JsonResponse(error, safe=False)


@api_view(['POST'])
def CommitTestEntryData(request):
    payload_dict = request.POST
    logger.info(message=f"payload_dict={payload_dict}", details=f"utilities.py CommitTestEntryData")
    action = payload_dict['action']
    logger.info(message=f"action={action}", details=f"utilities.py CommitTestEntryData")
    data_manager = DjangoDataManager()
    data_manager.payload = payload_dict

    results = {}

    if action in TEST_ENTRY_ACTIONS:
        try:
            data_manager.UpdateTestEntry()
        except Exception as e:
            msg = {"message": f"{e}", "success": False}
        else:
            msg = {"message": "Successfully committed test entry(s)", "success": True}
    else:
        msg = {"message": "invalid action passed", "success": False}

    results["message"] = msg
    return JsonResponse(results["message"], safe=False)


@api_view(['POST'])
def DeleteTestEntry(request):
    payload_dict = request.POST
    logger.info(message=f"payload_dict={payload_dict}", details=f"utilities.py DeleteTestEntry")
    action = payload_dict['action']
    logger.info(message=f"action={action}", details=f"utilities.py DeleteTestEntry")
    data_manager = DjangoDataManager()

    results = {}

    if action in TEST_ENTRY_ACTIONS:
        try:
            data_manager.DeleteTest(payload=payload_dict)
        except Exception as e:
            msg = {"message": f"{e}", "success": False}
        else:
            msg = {"message": "Successfully deleted test entry", "success": True}
    else:
        msg = {"message": "invalid action passed", "success": False}

    results["message"] = msg
    return JsonResponse(results["message"], safe=False)


@api_view(["POST"])
def ModifyEntry(request):
    payload = request.POST
    logger.info(message=f"payload={payload}", details=f"utilities.py ModifyEntry")

    table_objects = {
        "litho": Litho,
        "paper_test_reason": PaperTestReason,
        "paper_test_type": PaperTestType,
        "paper_test_position": PaperTestPosition,
        "combined_board_test_reason": CombinedBoardTestReason,
        "combined_board_test_layer": CombinedBoardTestLayer,
        "combined_board_test_type": CombinedBoardTestType,
    }

    results = {"status":"failure", "message": "Something went wrong"}

    all_plant_ids = Plant.objects.all()
    for plant in all_plant_ids:
        table_object = table_objects[f"{payload['table'][:-1]}"].objects.filter(code=payload['code'], plant=plant).first()
        try:
            if table_object:
                logger.info("Updating existing record")
                table_object.code = payload["code"]
                table_object.desc = payload["desc"]
                table_object.save()
                results = {"status": "success",
                                     "message": f"Updating existing record with code={table_object.code} and desc=({table_object.desc})"}
            else:
                logger.info("Creating new record")
                new_record = table_objects[payload['table'][:-1]](code=payload["code"], desc=payload["desc"], plant=plant)
                logger.info("Saving new record")
                results = {"status": "success",
                           "message": f"Created new record with code={new_record.code} and desc=({new_record.desc})"}
                new_record.save()
        except Exception as e:
            results = {"status": "failure",
                                 "message": f"Exception = {e}"}

    return JsonResponse(results)


@api_view(["POST"])
def RollVerification(request):
    payload = request.POST
    if not Plant.objects.filter(code=payload["plant"]).exists():
        return JsonResponse({"status": "failure", "message": "Plant doesn't exist", "data": ""})

    plant_obj = Plant.objects.filter(code=payload["plant"]).first()

    if Roll.objects.filter(roll_no=payload["roll_no"], plant=plant_obj).exists():
        roll = Roll.objects.filter(roll_no=payload["roll_no"], plant=plant_obj).first()
        # Copy Progress field names
        data = {}
        data["roll_no"] = roll.get_roll_no()
        data["inv_tcode"] = roll.paper_type.get_desc()
        data["grade"] = roll.grade.get_desc()
        data["vendor_name"] = roll.get_vendor_name()
        return JsonResponse({"status": "success", "message": "Roll data found in database", "data": data})

    try:
        roll_data = ProgressTableReads(
            payload={"action": "find_rolls", "plant": payload["plant"], "roll_no": payload["roll_no"]}
        )[0]
    except:
        return JsonResponse({"status": "failure",
                             "message": f"Data sent to Progress ERP was bad in some way plant={payload['plant']} | roll_no={payload['roll_no']}",
                             "data": ""})

    if not Vendor.objects.filter(code=roll_data["vendor_code"], desc=roll_data["vendor_name"],
                                 plant=plant_obj).exists():
        v = Vendor(code=roll_data["vendor_code"], desc=roll_data["vendor_name"], plant=plant_obj)
        logger.info("save vendor")
        v.save()

    if not PaperType.objects.filter(code=roll_data["inv_tcode"], plant=plant_obj).exists():
        p = PaperType(code=roll_data["inv_tcode"], plant=plant_obj)
        logger.info("save papertype")
        p.save()

    if not Grade.objects.filter(code=roll_data["grade"], plant=plant_obj).exists():
        g = Grade(code=roll_data["grade"], plant=plant_obj)
        logger.info("save grade")
        g.save()

    vendor_obj = Vendor.objects.filter(code=roll_data["vendor_code"], plant=plant_obj).first()
    paper_type_obj = PaperType.objects.filter(code=roll_data["inv_tcode"],
                                              plant=plant_obj).first()
    grade_obj = Grade.objects.filter(code=roll_data["grade"], plant=plant_obj).first()

    ###########################
    # Roll
    ###########################
    if not Roll.objects.filter(roll_no=roll_data["roll_no"], plant=plant_obj).exists():
        r = Roll(roll_no=roll_data["roll_no"], vroll_no=roll_data["vroll_no"],
                 tally_id=roll_data["talley_id"].strip(),
                 width=roll_data["actual_width"],
                 received_date=FormatDateForDatabase(roll_data["rec_date"]),
                 weight=roll_data["orig_weight"],
                 linear_foot=roll_data["orig_linear_f"], msf=roll_data["orig_msf"],
                 cost_by_ton=roll_data["cost_by_ton"], cost_by_msf=roll_data["cost_by_msf"],
                 mill=roll_data["mill"], moisture=roll_data["moisture"],
                 vendor=vendor_obj, paper_type=paper_type_obj, grade=grade_obj,
                 plant=plant_obj)
        logger.info("save roll")
        r.save()

    roll = Roll.objects.filter(roll_no=roll_data["roll_no"], plant=plant_obj).first()
    data = {}
    data["roll_no"] = roll.get_roll_no()
    data["inv_tcode"] = roll.paper_type.get_desc()
    data["grade"] = roll.grade.get_desc()
    data["vendor_name"] = roll.get_vendor_name()
    return JsonResponse({"status": "success", "message": "Roll data found in database", "data": data})

@api_view(["POST"])
def FetchTargetModel(request):
    payload = request.POST
    # TODO - Potentially may need to get enhanced to go beyond key-value pairs, but is adequate now (03/06/2025)

    # Variables
    key_value_pairs = {}

    # Ensure appropriate plane is selected
    try:
        plant_obj = Plant.objects.filter(code=payload["plant_code"]).first()
    except:
        return JsonResponse({"status": "failed", "message": f"creation of plant object failed {payload['plant_code']}"})

    # Fetch the database records
    if payload["target_model"] == "paper_test_type":
        target_model = PaperTestType.objects.filter(plant=plant_obj).all()
    elif payload["target_model"] == "paper_test_reason":
        target_model = PaperTestReason.objects.filter(plant=plant_obj).all()
    elif payload["target_model"] == "paper_test_position":
        target_model = PaperTestPosition.objects.filter(plant=plant_obj).all()
    elif payload["target_model"] == "litho":
        target_model = Litho.objects.filter(plant=plant_obj).all()
    elif payload["target_model"] == "combined_test_type":
        target_model = CombinedBoardTestType.objects.filter(plant=plant_obj).all()
    elif payload["target_model"] == "combined_test_reason":
        target_model = CombinedBoardTestReason.objects.filter(plant=plant_obj).all()
    elif payload["target_model"] == "combined_test_layer":
        target_model = CombinedBoardTestLayer.objects.filter(plant=plant_obj).all()
    else:
        return JsonResponse({"status": "failed", "message": f"No appropriate target model was provided! ({payload['target_model']})"})

    # Aggregate the data into a key-value pair setup
    for records in target_model:
        key_value_pairs[records.code] = records.desc

    return JsonResponse({"status": "success", "key_value_pairs": key_value_pairs})
