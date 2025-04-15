# import_paper_csv.py
import csv
from django.core.management.base import BaseCommand
from local.Logging import Logger
from local.globals import DEFAULT_PREFERENCES
from api.services.ProgressTableReads import ProgressTableReads
from api.models.Account import Account
from api.models.Templates import Plant
from api.models.TestEntry import CombinedBoardTest, PaperTest
from api.models.Tracking import Order, Roll
from api.models.Utility import SpecialInstructionCode, Customer, Flute, Corrugator, OrderTestCode, \
    CombinedBoardTestReason, CombinedBoardTestType, CombinedBoardTestLayer, Vendor, PaperType, Grade, Litho, \
    PaperTestPosition, PaperTestReason, PaperTestType

from time import strptime

logger = Logger(__file__)


def format_date(init_date_string):
    from datetime import datetime
    # Convert the date from MM/DD/YY to YYYY-MM-DD
    date_object = datetime.strptime(init_date_string, '%m/%d/%Y')
    formatted_date = date_object.strftime('%Y-%m-%d')
    return formatted_date


class Command(BaseCommand):
    help = "Import data from CSV file into the database"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                logger.debug(message=f"row={row}")
                created_at = format_date(
                    str(strptime(row["created_month"], "%b").tm_mon) + "/" + row["created_day"] + "/" + row["created_year"])
                username = "riess"
                plant_code = row["plant_code"].lower()
                roll_no = row["roll_no"]
                vendor_name = row["vendor_name"]
                paper_type_code = row["paper_type_code"]
                grade = row["grade"]
                tally_id = row["tally_id"]

                # #####################################################################
                # # Simply here to update the time, uncomment if needed
                # #####################################################################
                plant_obj = Plant.objects.filter(code=plant_code).first()
                roll_obj = Roll.objects.filter(roll_no=roll_no, plant=plant_obj).first()

                #### account_obj = Account.objects.filter(username=username).first()
                ####
                #### #### Update username
                #### list_of_test_types = ["caliper", "basis_weight", "brightness", "cobb_2_minute", "cobb_30_minute",
                ####                       "concora", "dyne_base", "dyne_top", "i_bond", "moisture", "mullen",
                ####                       "peel_opposite", "peel_true", "porosity", "ring_crush_cd", "scott_bond", "scuff",
                ####                       "slide_angle", "smoothness", "stfi"]
                ####
                #### for test_type in list_of_test_types:
                ####     count_key = test_type + "_count"
                ####     values_key = test_type
                ####
                ####     if row[values_key] == "":
                ####         continue
                ####
                ####     self.stdout.write(self.style.WARNING(f"Found test_type {values_key} with a value {row[values_key]}"))
                ####     test_type_obj = PaperTestType.objects.filter(code=test_type, plant=plant_obj).first()
                ####
                ####     for test_no in range(0, int(row[count_key])):
                ####         self.stdout.write(self.style.WARNING(f"test_no={test_no} | row[count_key]={row[count_key]}"))
                ####         test_entry_value = row[values_key].split(",")[test_no]
                ####
                ####         paper_test = PaperTest.objects.filter(test_value=test_entry_value, test_type=test_type_obj,
                ####                                                         roll=roll_obj, plant=plant_obj).first()
                ####         if paper_test:
                ####             paper_test.author = account_obj
                ####             self.stdout.write(self.style.WARNING(f"paper_test.author={account_obj.username}"))
                ####             paper_test.save()
                ####             self.stdout.write(self.style.SUCCESS(f"Success"))
                ####
                #### continue

                ##### Add tally_id
                ##### if roll_obj:
                #####     roll_obj.tally_id = tally_id.strip()
                #####     self.stdout.write(self.style.WARNING(f"Setting tally_id={tally_id}"))
                #####     roll_obj.save()
                #####     self.stdout.write(self.style.SUCCESS(f"Tally id set"))
                #####
                ##### continue
                # list_of_test_types = ["caliper", "basis_weight", "brightness", "cobb_2_minute", "cobb_30_minute",
                #                       "concora", "dyne_base", "dyne_top", "i_bond", "moisture", "mullen",
                #                       "peel_opposite", "peel_true", "porosity", "ring_crush_cd", "scott_bond", "scuff",
                #                       "slide_angle", "smoothness", "stfi"]
                #
                # for test_type in list_of_test_types:
                #     count_key = test_type + "_count"
                #     values_key = test_type
                #
                #     if row[values_key] == "":
                #         continue
                #
                #     self.stdout.write(self.style.WARNING(f"Found test_type {values_key} with a value {row[values_key]}"))
                #     test_type_obj = PaperTestType.objects.filter(code=test_type, plant=plant_obj).first()
                #
                #     for test_no in range(0, int(row[count_key])):
                #         test_entry_value = row[values_key].split(",")[test_no]
                #
                #         paper_test = PaperTest.objects.filter(test_value=test_entry_value, test_type=test_type_obj,
                #                                                         roll=roll_obj, plant=plant_obj).first()
                #         if paper_test:
                #             paper_test.created_at = created_at + " 00:00:00.000000Z"
                #             self.stdout.write(self.style.SUCCESS(f"paper_test.test_value={paper_test.test_value}"))
                #             self.stdout.write(self.style.SUCCESS(f"Updating time created_at={created_at}"))
                #             paper_test.save()
                #
                # continue
                # if not paper_test:
                #     self.stdout.write(self.style.WARNING(f"Failed to find paper_test"))
                # elif len(created_at) == 27:
                #     self.stdout.write(self.style.SUCCESS(f"roll_obj={roll_obj}"))
                #     self.stdout.write(self.style.WARNING(
                #         f"Updating order={roll_obj.roll_no} | test_type={test_type_obj.desc} | combined_test={combined_board_test.test_value} | created_at={created_at}"))
                #     combined_board_test.created_at = created_at
                #     combined_board_test.save()
                #     self.stdout.write(self.style.SUCCESS(f"Updated"))
                # else:
                #     self.stdout.write(self.style.WARNING(f"created_at len not 26 {created_at} {len(created_at)}"))
                #     return
                #
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

                    if not Vendor.objects.filter(code=roll_data["vendor_code"].lower(), desc=roll_data["vendor_name"],
                                                 plant=plant_obj).exists():
                        v = Vendor(code=roll_data["vendor_code"].lower(), desc=roll_data["vendor_name"],
                                   plant=plant_obj)
                        logger.info("save vendor")
                        v.save()

                    if not PaperType.objects.filter(code=roll_data["inv_tcode"].lower(), plant=plant_obj).exists():
                        p = PaperType(code=roll_data["inv_tcode"].lower(), plant=plant_obj)
                        logger.info("save papertype")
                        p.save()

                    if not Grade.objects.filter(code=roll_data["grade"].lower(), plant=plant_obj).exists():
                        g = Grade(code=roll_data["grade"].lower(), plant=plant_obj)
                        logger.info("save grade")
                        g.save()

                    vendor_obj = Vendor.objects.filter(code=roll_data["vendor_code"], plant=plant_obj).first()
                    paper_type_obj = PaperType.objects.filter(code=roll_data["inv_tcode"],
                                                              plant=plant_obj).first()
                    grade_obj = Grade.objects.filter(code=roll_data["grade"], plant=plant_obj).first()

                    r = Roll(roll_no=roll_data["roll_no"], vroll_no=roll_data["vroll_no"],
                             width=roll_data["actual_width"], received_date=format_date(roll_data["rec_date"]),
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
                if not PaperTestReason.objects.filter(code="null", plant=plant_obj).exists:
                    p = PaperTestReason(code="null", desc="null", plant=plant_obj)
                    logger.info("saving paper_test_reason")
                    p.save()

                if not PaperTestPosition.objects.filter(code="null", plant=plant_obj).exists:
                    p = PaperTestPosition(code="null", desc="null",
                                          plant=plant_obj)
                    logger.info("saving paper_test_position")
                    p.save()

                list_of_test_types = ["caliper", "basis_weight", "brightness", "cobb_2_minute", "cobb_30_minute",
                                      "concora", "dyne_base", "dyne_top", "i_bond", "moisture", "mullen",
                                      "peel_opposite", "peel_true", "porosity", "ring_crush_cd", "scott_bond", "scuff",
                                      "slide_angle", "smoothness", "stfi"]

                roll_obj = Roll.objects.filter(roll_no=roll_no, plant=plant_obj).first()
                paper_test_reason_obj = PaperTestReason.objects.filter(code="null", plant=plant_obj).first()
                paper_test_position_obj = PaperTestPosition.objects.filter(code="null", plant=plant_obj).first()

                for test_type in list_of_test_types:
                    count_key = test_type + "_count"
                    values_key = test_type
                    if row[values_key] == "":
                        continue

                    if not PaperTestType.objects.filter(code=values_key, plant=plant_obj).exists():
                        p = PaperTestType(code=values_key, desc=values_key.replace("_", " ").capitalize(),
                                          plant=plant_obj)
                        logger.info("saving paper_test_type")
                        p.save()

                    paper_test_type_obj = PaperTestType.objects.filter(code=values_key, plant=plant_obj).first()

                    if int(row[count_key]) > 1:
                        # Perform multiple test entries
                        for test_no in range(0, int(row[count_key])):
                            test_entry_value = row[values_key].split(",")[test_no]
                            new_test = PaperTest(test_value=test_entry_value, roll=roll_obj, author=account_obj,
                                                 created_at=created_at,
                                                 test_type=paper_test_type_obj, test_reason=paper_test_reason_obj,
                                                 test_position=paper_test_position_obj, plant=plant_obj)
                            new_test.save()
                            self.stdout.write(self.style.SUCCESS(
                                f"saved test entry value={test_entry_value} for roll={roll_obj.roll_no}"))
                    else:
                        test_entry_value = row[values_key]
                        new_test = PaperTest(test_value=test_entry_value, roll=roll_obj, author=account_obj,
                                             created_at=created_at,
                                             test_type=paper_test_type_obj, test_reason=paper_test_reason_obj,
                                             test_position=paper_test_position_obj, plant=plant_obj)
                        new_test.save()
                        self.stdout.write(self.style.SUCCESS(f"saved test entry value={test_entry_value} for roll={roll_obj.roll_no}"))

            self.stdout.write(self.style.SUCCESS("Data imported successfully."))
