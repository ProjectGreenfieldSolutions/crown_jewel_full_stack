from django.db.models import AutoField, CharField, DateField, DateTimeField, DecimalField, FloatField, IntegerField, PositiveSmallIntegerField
from django.db.models import ForeignKey, Model
from django.db.models import CASCADE, RESTRICT
from django.db.models.constraints import UniqueConstraint
from .Templates import KeyValuePairModel, StandardModel
from django.conf import settings
from local.Logging import Logger
logger = Logger(__file__)

"""
Determine defaults, if any
Fetching of occasionally updated data (aka syncing with ERP)
"""

class Litho(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_litho')
        ]

    def get_litho_point(self):
        logger.debug(message=f"Returning self.code {self.code}")
        return self.code

class Customer(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_customer')
        ]
    def get_cust_no(self):
        logger.debug(message=f"Returning self.code {self.code}")
        return self.code

    def get_name(self):
        logger.debug(message=f"Returning self.desc {self.desc}")
        return self.desc

class Corrugator(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_corrugator')
        ]
    def get_id(self):
        logger.debug(message=f"Returning self.code {self.code}")
        return self.code

    def get_name(self):
        logger.debug(message=f"Returning self.desc {self.desc}")
        return self.desc

class Vendor(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_vendor')
        ]
    def get_name(self):
        logger.debug(message=f"Returning self.desc {self.desc}")
        return self.desc

class Flute(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_flute')
        ]

class Grade(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_grade')
        ]

class OrderTestCode(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_order_test_code')
        ]

class PaperType(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_paper_type')
        ]

class SpecialInstructionCode(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_special_instruction_code')
        ]

class PaperTestReason(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_paper_test_reason')
        ]

class PaperTestPosition(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_paper_test_position')
        ]

class PaperTestType(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_paper_test_type')
        ]

class CombinedBoardTestReason(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_combined_board_test_reason')
        ]

class CombinedBoardTestLayer(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_combined_board_test_layer')
        ]

class CombinedBoardTestType(KeyValuePairModel):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['code', 'plant'], name='unique_code_plant_combined_board_test_type')
        ]
