# import_combined_csv.py
import csv
from django.core.management.base import BaseCommand
from local.Logging import Logger
from local.globals import DEFAULT_PREFERENCES
from api.services.ProgressTableReads import ProgressTableReads
from api.models.Account import Account
from api.models.Templates import Plant
from api.models.TestEntry import CombinedBoardTest
from api.models.Tracking import Order, Roll
from api.models.Utility import SpecialInstructionCode, Customer, Flute, Corrugator, OrderTestCode, \
    CombinedBoardTestReason, CombinedBoardTestType, CombinedBoardTestLayer, Vendor, PaperType, Grade, Litho

logger = Logger(__file__)


def format_date(init_date_string):
    from datetime import datetime
    # Convert the date from MM/DD/YY to YYYY-MM-DD
    date_object = datetime.strptime(init_date_string, '%m/%d/%y')
    formatted_date = date_object.strftime('%Y-%m-%d')
    return formatted_date


class Command(BaseCommand):
    help = "Import data from CSV file into the database"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        # # Remove duplicates
        # from django.db.models import Count
        # from api.models.Utility import PaperTestPosition, PaperTestReason, PaperTestType, CombinedBoardTestReason, \
        #     CombinedBoardTestLayer, CombinedBoardTestType
        # duplicate_entries = CombinedBoardTestLayer.objects.values('code', "plant").annotate(count=Count('id')).filter(
        #     count__gt=1)
        #
        # for entry in duplicate_entries:
        #     self.stdout.write(self.style.WARNING(f"entry={entry}"))
        #     duplicates = CombinedBoardTestLayer.objects.filter(code=entry['code'], plant=entry["plant"])
        #     duplicates.exclude(pk=duplicates.first().pk).delete()
        #     self.stdout.write(self.style.SUCCESS(f"Deleted"))
        #
        # return

        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            order_data = {}
            order_data["order_no"] = None
            for row in reader:
                logger.debug(message=f"row={row}")

                username = row["account.username"]
                order_no = row["order.order_no"]
                plant_code = row["plant"]
                test_value = row["combinedboardtest.test_value"]
                test_reason = "normal"
                test_type = row["combinedboardtest.test_type.desc"]
                created_at = row["combinedboardtest.created_at"].replace("T", " ")
                layer_1 = row["combinedboardtest.layer_1"]
                layer_2 = row["combinedboardtest.layer_2"]
                layer_3 = row["combinedboardtest.layer_3"]
                layer_4 = row["combinedboardtest.layer_4"]
                layer_5 = row["combinedboardtest.layer_5"]
                layer_6 = ""
                layer_7 = ""
                roll_1 = row["roll_1.roll_no"]
                roll_2 = row["roll_2.roll_no"]
                roll_3 = row["roll_3.roll_no"]
                roll_4 = row["roll_4.roll_no"]
                roll_5 = row["roll_5.roll_no"]
                roll_6 = ""
                roll_7 = ""

                # #####################################################################
                # # Simply here to update the time, uncomment if needed
                # #####################################################################
                # plant_obj = Plant.objects.filter(code=plant_code).first()
                # order_obj = Order.objects.filter(order_no=order_no, plant=plant_obj).first()
                # test_type_obj = CombinedBoardTestType.objects.filter(desc=test_type, plant=plant_obj).first()
                # combined_board_test = CombinedBoardTest.objects.filter(test_value=test_value, test_type=test_type_obj, order=order_obj, plant=plant_obj).first()
                #
                # if not combined_board_test:
                #     self.stdout.write(self.style.WARNING(f"Failed to find combined_board_test"))
                # elif len(created_at) == 27:
                #     self.stdout.write(self.style.SUCCESS(f"order_obj={order_obj}"))
                #     self.stdout.write(self.style.WARNING(f"Updating order={order_obj.order_no} | test_type={test_type_obj.desc} | combined_test={combined_board_test.test_value} | created_at={created_at}"))
                #     combined_board_test.created_at = created_at
                #     combined_board_test.save()
                #     self.stdout.write(self.style.SUCCESS(f"Updated"))
                # else:
                #     self.stdout.write(self.style.WARNING(f"created_at len not 26 {created_at} {len(created_at)}"))
                #     return
                # continue

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
                # TODO - change for actual
                number_of_entries = 8
                number_of_entries = 6
                for n in range(1, number_of_entries):
                    roll_no = row["roll_" + str(n) + ".roll_no"]
                    test_layer = row["combinedboardtest.layer_" + str(n)]
                    if not roll_no == "":
                        self.stdout.write(self.style.WARNING(f"roll_no={roll_no} | test_layer={test_layer}"))
                        if Roll.objects.filter(roll_no=roll_no, plant=plant_obj).exists():
                            self.stdout.write(self.style.SUCCESS(f"Found"))
                            continue
                        else:
                            self.stdout.write(self.style.SUCCESS(f"Not found"))
                            continue

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

                        self.stdout.write(self.style.WARNING(f"Checking for roll object after roll_order"))
                        if not Roll.objects.filter(roll_no=roll_data["roll_no"], plant=plant_obj).exists():
                            r = Roll(roll_no=roll_data["roll_no"], vroll_no=roll_data["vroll_no"],
                                     width=roll_data["actual_width"], received_date=format_date(roll_data["rec_date"]),
                                     weight=roll_data["orig_weight"],
                                     linear_foot=roll_data["orig_linear_f"], msf=roll_data["orig_msf"],
                                     cost_by_ton=roll_data["cost_by_ton"], cost_by_msf=roll_data["cost_by_msf"],
                                     mill=roll_data["mill"], moisture=roll_data["moisture"],
                                     vendor=vendor_obj, paper_type=paper_type_obj, grade=grade_obj,
                                     plant=plant_obj)
                            logger.info("save roll")
                            r.save()

                        if not test_layer == "":
                            if not CombinedBoardTestLayer.objects.filter(code=test_layer.lower().replace(" ", "_"),
                                                                         plant=plant_obj).exists():
                                c = CombinedBoardTestLayer(code=test_layer.lower().replace(" ", "_"), desc=test_layer,
                                                           plant=plant_obj)
                                logger.info("save test_layer")
                                c.save()

                            test_layer_obj = CombinedBoardTestLayer.objects.filter(
                                code=test_layer.lower().replace(" ", "_"), plant=plant_obj).first()

                # self.stdout.write(self.style.WARNING(f"Searching for {roll_1}"))
                # order_obj = Order.objects.filter(order_no=order_no, plant=plant_obj).first()
                # test_reason_obj = CombinedBoardTestReason.objects.filter(code="normal", plant=plant_obj).first()
                # test_type_obj = CombinedBoardTestType.objects.filter(code=test_type.lower().replace(" ", "_"),
                #                                                      plant=plant_obj).first()
                # roll_1_obj = Roll.objects.filter(roll_no=roll_1, plant=plant_obj).first()
                # combined_board_test = CombinedBoardTest.objects.filter(test_value=test_value, order=order_obj,
                #                                                        author=account_obj, test_reason=test_reason_obj,
                #                                                        test_type=test_type_obj, created_at=created_at,
                #                                                        plant=plant_obj).first()
                #
                # if combined_board_test:
                #     self.stdout.write(self.style.WARNING(f"Combined board test found"))
                #     combined_board_test.test_roll_1 = roll_1_obj
                #     combined_board_test.save()
                #     self.stdout.write(self.style.SUCCESS(f"roll_1_obj={roll_1_obj}"))
                #     self.stdout.write(self.style.SUCCESS(f"combined_board_test={combined_board_test}"))
                #     self.stdout.write(self.style.SUCCESS(f"combined_board_test.test_roll_1={combined_board_test.test_roll_1}"))
                #     self.stdout.write(self.style.SUCCESS(f"Success"))
                # else:
                #     self.stdout.write(self.style.WARNING(f"Not test found"))
                #
                # continue
                #####################################################################
                # Order Related Tables
                #####################################################################
                if not order_no == order_data["order_no"]:
                    self.stdout.write(self.style.WARNING(f"Loading in order data"))
                    order_data = ProgressTableReads(
                        payload={"action": "search_order", "plant": plant_code, "order": order_no})

                self.stdout.write(self.style.WARNING(f"Customer"))
                if not Customer.objects.filter(code=order_data["cust_no"], plant=plant_obj).exists():
                    c = Customer(code=order_data["cust_no"], desc=order_data["customer_name"], plant=plant_obj)
                    logger.info("save customer")
                    c.save()

                self.stdout.write(self.style.WARNING(f"Flute"))
                if not Flute.objects.filter(code=order_data["flute_code"], desc=order_data["flute_flute_desc"],
                                            plant=plant_obj).exists():
                    f = Flute(code=order_data["flute_code"], desc=order_data["flute_flute_desc"], plant=plant_obj)
                    logger.info("save flute")
                    f.save()

                self.stdout.write(self.style.WARNING(f"Corrugator"))
                if not Corrugator.objects.filter(desc=order_data["corrugator_corru_name"], plant=plant_obj).exists():
                    c = Corrugator(code=order_data["corru_id"], desc=order_data["corrugator_corru_name"],
                                   plant=plant_obj)
                    logger.info("save corrugator")
                    c.save()

                self.stdout.write(self.style.WARNING(f"OrderTestCode"))
                if not OrderTestCode.objects.filter(code=order_data["test_code"], plant=plant_obj).exists():
                    o = OrderTestCode(code=order_data["test_code"], plant=plant_obj)
                    logger.info("save order")
                    o.save()

                self.stdout.write(self.style.WARNING(f"SpecialInstructionCode"))
                if not SpecialInstructionCode.objects.filter(code=order_data["spec_code"], plant=plant_obj).exists():
                    s = SpecialInstructionCode(code=order_data["spec_code"], plant=plant_obj)
                    logger.info("save special_instruction_code")
                    s.save()

                #####################################################################
                # Acquire Objects For Order Table
                #####################################################################
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
                self.stdout.write(self.style.WARNING(f"Order"))
                if not Order.objects.filter(order_no=order_data["order_no"], plant=plant_obj).exists():
                    o = Order(order_no=order_data["order_no"], order_date=format_date(order_data["order_date"]),
                              cust_po=order_data["cust_po"], ship_no=order_data["ship_no"],
                              ship_date=format_date(order_data["ship_date"]), width=order_data["width"],
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
                # if not CombinedBoardTestReason.objects.filter(code=test_reason.lower().replace(" ", "_"), desc=test_reason, plant=plant_obj).exists():
                #     c = CombinedBoardTestReason(code=test_reason.lower().replace(" ", "_"), desc=test_reason,
                #                                 plant=plant_obj)
                #     logger.info("save combined board test reason")
                #     c.save()

                test_reason_obj = CombinedBoardTestReason.objects.filter(code="normal", plant=plant_obj).first()

                self.stdout.write(self.style.WARNING(f"CombinedBoardTestType"))
                if not CombinedBoardTestType.objects.filter(code=test_type.lower().replace(" ", "_"),
                                                            plant=plant_obj).exists():
                    logging.info(f'No combined board test type found {test_type.lower().replace(" ", "_")}')
                    c = CombinedBoardTestType(code=test_type.lower().replace(" ", "_"), desc=test_type, plant=plant_obj)
                    logger.info("save combined board test type")
                    c.save()

                test_type_obj = CombinedBoardTestType.objects.filter(code=test_type.lower().replace(" ", "_"),
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
                # Commit Test Entry To Database
                #####################################################################
                new_test = CombinedBoardTest(
                    test_value=test_value, order=order_obj, author=account_obj, test_reason=test_reason_obj,
                    test_type=test_type_obj, created_at=created_at, plant=plant_obj,
                    test_layer_1=test_layer_1_obj, test_layer_2=test_layer_2_obj, test_layer_3=test_layer_3_obj,
                    test_layer_4=test_layer_4_obj, test_layer_5=test_layer_5_obj, test_layer_6=test_layer_6_obj,
                    test_layer_7=test_layer_7_obj, test_litho_1=litho_obj, test_roll_1=roll_1_obj,
                    test_roll_2=roll_2_obj,
                    test_roll_3=roll_3_obj, test_roll_4=roll_4_obj, test_roll_5=roll_5_obj, test_roll_6=roll_6_obj,
                    test_roll_7=roll_7_obj)
                logger.info("saving combined test entry")
                self.stdout.write(self.style.WARNING(
                    f"Saved test entry order_no={order_obj.order_no} | value={test_value} | test_type={test_type_obj.desc}"))
                new_test.save()
                self.stdout.write(self.style.SUCCESS(f"Saved"))

        self.stdout.write(self.style.SUCCESS("Data imported successfully."))
