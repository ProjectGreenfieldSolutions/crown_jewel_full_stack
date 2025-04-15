from django.conf import settings
from django.db.models import AutoField, CharField, DateField, DateTimeField, DecimalField, FloatField, IntegerField, PositiveSmallIntegerField
from django.db.models import ForeignKey, Model
from django.db.models import CASCADE, RESTRICT
from django.db.models.constraints import UniqueConstraint
from .Account import Account
from .Templates import StandardModel
from .Utility import PaperTestReason, PaperTestPosition, PaperTestType, CombinedBoardTestReason, CombinedBoardTestLayer, CombinedBoardTestType, Litho
from .Tracking import Roll, Order, LithoPaper
from local.Logging import Logger
logger = Logger(__file__)


class PaperTest(StandardModel):
    test_value = FloatField()

    # Foreign Keys
    roll = ForeignKey(Roll, on_delete=CASCADE)
    test_reason = ForeignKey(PaperTestReason, on_delete=RESTRICT)
    test_position = ForeignKey(PaperTestPosition, on_delete=RESTRICT)
    author = ForeignKey(Account, on_delete=RESTRICT)
    test_type = ForeignKey(PaperTestType, on_delete=RESTRICT)

    def get_plant_code(self):
        logger.debug(message=f"Returning self.plant.code {self.plant.code}")
        return self.plant.code

    def get_plant_desc(self):
        logger.debug(message=f"Returning self.plant.desc {self.plant.desc}")
        return self.plant.desc

    def get_paper_type_code(self):
        logger.debug(message=f"Returning self.roll.get_paper_type_code() {self.roll.get_paper_type_code()}")
        return self.roll.get_paper_type_code()

    def get_paper_type_desc(self):
        logger.debug(message=f"Returning self.roll.get_paper_type_desc() {self.roll.get_paper_type_desc()}")
        return self.roll.get_paper_type_desc()

    def get_roll_width(self):
        logger.debug(message=f"Returning self.roll.width {self.roll.width}")
        return self.roll.width

    def get_roll_no(self):
        logger.debug(message=f"Returning self.roll.get_roll_no {self.roll.roll_no}")
        return self.roll.get_roll_no()

    def get_vroll_no(self):
        logger.debug(message=f"Returning self.roll.get_vroll_no {self.roll.vroll_no}")
        return self.roll.get_vroll_no()

    def get_roll_grade_code(self):
        logger.debug(message=f"Returning self.roll.get_grade_code() {self.roll.get_grade_code()}")
        return self.roll.get_grade_code()

    def get_roll_grade_desc(self):
        logger.debug(message=f"Returning self.roll.get_grade_desc() {self.roll.get_grade_desc()}")
        return self.roll.get_grade_desc()

    def get_author(self):
        logger.debug(message=f"Returning author {self.author.username}")
        return self.author.username

    def get_test_reason_code(self):
        logger.debug(message=f"Returning test_reason.code {self.test_reason.code}")
        return self.test_reason.code

    def get_test_reason_desc(self):
        logger.debug(message=f"Returning test_reason.desc {self.test_reason.desc}")
        return self.test_reason.desc

    def get_test_type_code(self):
        logger.debug(message=f"Returning test_type.code {self.test_type.code}")
        return self.test_type.code

    def get_test_type_desc(self):
        logger.debug(message=f"Returning test_type.desc {self.test_type.desc}")
        return self.test_type.desc

    def get_test_position_code(self):
        logger.debug(message=f"Returning test_position.code {self.test_position.code}")
        return self.test_position.code

    def get_test_position_desc(self):
        logger.debug(message=f"Returning test_position.desc {self.test_position.desc}")
        return self.test_position.desc

class CombinedBoardTest(StandardModel):
    test_value = FloatField()

    # Foreign Keys
    order = ForeignKey(Order, on_delete=CASCADE)
    author = ForeignKey(Account, on_delete=RESTRICT)
    test_reason = ForeignKey(CombinedBoardTestReason, on_delete=RESTRICT)
    test_type = ForeignKey(CombinedBoardTestType, on_delete=RESTRICT)

    test_layer_1 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_1")
    test_layer_2 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_2")
    test_layer_3 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_3")
    test_layer_4 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_4")
    test_layer_5 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_5")
    test_layer_6 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_6")
    test_layer_7 = ForeignKey(CombinedBoardTestLayer, on_delete=RESTRICT, null=True, related_name="layer_7")
    test_litho_1 = ForeignKey(Litho, on_delete=RESTRICT, null=True, related_name="litho_point")
    test_roll_1 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_1")
    test_roll_2 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_2")
    test_roll_3 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_3")
    test_roll_4 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_4")
    test_roll_5 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_5")
    test_roll_6 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_6")
    test_roll_7 = ForeignKey(Roll, on_delete=RESTRICT, null=True, related_name="roll_7")

    def get_plant_code(self):
        logger.debug(message=f"Returning self.plant.code {self.plant.code}")
        return self.plant.code

    def get_plant_desc(self):
        logger.debug(message=f"Returning self.plant.desc {self.plant.desc}")
        return self.plant.desc

    def get_order_no(self):
        logger.debug(message=f"Returning order_no {self.order.order_no}")
        return self.order.order_no

    def get_flute_code(self):
        logger.debug(message=f"Returning self.order.get_flute_code() {self.order.get_flute_code()}")
        return self.order.get_flute_code()

    def get_flute_desc(self):
        logger.debug(message=f"Returning self.order.get_flute_desc() {self.order.get_flute_desc()}")
        return self.order.get_flute_desc()

    def get_order_test_code(self):
        logger.debug(message=f"Returning self.order.get_order_test_code() {self.order.get_order_test_code()}")
        return self.order.get_order_test_code()

    def get_roll_no(self):
        logger.debug(message=f"Returning self.roll.roll_no {self.roll.roll_no}")
        return self.roll.roll_no

    def get_vroll_no(self):
        logger.debug(message=f"Returning self.roll.vroll_no {self.roll.vroll_no}")
        return self.roll.vroll_no

    def get_litho_point(self):
        logger.debug(message=f"Returning self.litho.get_litho_point() {self.litho.get_litho_point()}")
        return self.litho.get_litho_point()

    def get_author(self):
        logger.debug(message=f"Returning author {self.author.username}")
        return self.author.username

    def get_test_reason_code(self):
        logger.debug(message=f"Returning test_reason.code {self.test_reason.code}")
        return self.test_reason.code

    def get_test_reason_desc(self):
        logger.debug(message=f"Returning test_reason.desc {self.test_reason.desc}")
        return self.test_reason.desc

    def get_test_type_code(self):
        logger.debug(message=f"Returning test_type.code {self.test_type.code}")
        return self.test_type.code

    def get_test_type_desc(self):
        logger.debug(message=f"Returning test_type.desc {self.test_type.desc}")
        return self.test_type.desc

class LithoPaperTest(StandardModel):
    test_value = FloatField()

    # Foreign Keys
    litho_paper = ForeignKey(LithoPaper, on_delete=CASCADE)
    test_reason = ForeignKey(PaperTestReason, on_delete=RESTRICT)
    test_position = ForeignKey(PaperTestPosition, on_delete=RESTRICT)
    author = ForeignKey(Account, on_delete=RESTRICT)
    test_type = ForeignKey(PaperTestType, on_delete=RESTRICT)

    def get_litho_paper_uuid(self):
        logger.debug(message=f"Returning self.litho_paper.litho_uuid")
        return self.litho_paper.litho_uuid

    def get_litho_paper_pt(self):
        logger.debug(message=f"Returning self.litho_paper.litho_pt")
        return self.litho_paper.litho_pt

    def get_plant_code(self):
        logger.debug(message=f"Returning self.plant.code {self.plant.code}")
        return self.plant.code

    def get_plant_desc(self):
        logger.debug(message=f"Returning self.plant.desc {self.plant.desc}")
        return self.plant.desc

    def get_author(self):
        logger.debug(message=f"Returning author {self.author.username}")
        return self.author.username

    def get_test_reason_code(self):
        logger.debug(message=f"Returning test_reason.code {self.test_reason.code}")
        return self.test_reason.code

    def get_test_reason_desc(self):
        logger.debug(message=f"Returning test_reason.desc {self.test_reason.desc}")
        return self.test_reason.desc

    def get_test_type_code(self):
        logger.debug(message=f"Returning test_type.code {self.test_type.code}")
        return self.test_type.code

    def get_test_type_desc(self):
        logger.debug(message=f"Returning test_type.desc {self.test_type.desc}")
        return self.test_type.desc

    def get_test_position_code(self):
        logger.debug(message=f"Returning test_position.code {self.test_position.code}")
        return self.test_position.code

    def get_test_position_desc(self):
        logger.debug(message=f"Returning test_position.desc {self.test_position.desc}")
        return self.test_position.desc

