from django.conf import settings
from django.db.models import AutoField, CharField, DateField, DateTimeField, DecimalField, FloatField, IntegerField, PositiveSmallIntegerField
from django.db.models import ForeignKey, Model
from django.db.models import CASCADE, RESTRICT
from django.db.models.constraints import UniqueConstraint
from .Templates import StandardModel
from .Utility import Flute, Customer, Corrugator, Vendor, OrderTestCode, PaperType, Grade, SpecialInstructionCode, Litho
from local.Logging import Logger
logger = Logger(__file__)


class Roll(StandardModel):
    roll_no = CharField(max_length=20, unique=True)
    vroll_no = CharField(max_length=64, unique=True)
    tally_id = CharField(max_length=64, null=True)
    width = DecimalField(max_digits=10, decimal_places=2)
    received_date = DateField()
    weight = IntegerField()
    linear_foot = IntegerField()
    msf = DecimalField(max_digits=11, decimal_places=2)
    cost_by_ton = DecimalField(max_digits=10, decimal_places=2)
    cost_by_msf = DecimalField(max_digits=10, decimal_places=2)
    mill = CharField(max_length=20)
    moisture = DecimalField(max_digits=10, decimal_places=2)

    # Foreign Keys
    vendor = ForeignKey(Vendor, on_delete=RESTRICT)
    paper_type = ForeignKey(PaperType, on_delete=RESTRICT)
    grade = ForeignKey(Grade, on_delete=RESTRICT)

    def get_paper_type_code(self):
        logger.debug(message=f"Returning self.paper_type.code {self.paper_type.code}")
        return self.paper_type.code

    def get_paper_type_desc(self):
        logger.debug(message=f"Returning self.paper_type.desc {self.paper_type.desc}")
        return self.paper_type.desc

    def get_roll_no(self):
        logger.debug(message=f"Returning self.roll_no {self.roll_no}")
        return self.roll_no

    def get_vroll_no(self):
        logger.debug(message=f"Returning self.vroll_no {self.vroll_no}")
        return self.vroll_no

    def get_grade_code(self):
        logger.debug(message=f"Returning self.grade.code {self.grade.code}")
        return self.grade.code

    def get_grade_desc(self):
        logger.debug(message=f"Returning self.grade.desc {self.grade.desc}")
        return self.grade.desc

    def get_vendor_code(self):
        logger.debug(message=f"Returning self.vendor.code {self.vendor.code}")
        return self.vendor.code

    def get_vendor_name(self):
        logger.debug(message=f"Returning self.vendor.desc {self.vendor.desc}")
        return self.vendor.desc

class Order(StandardModel):
    order_no = CharField(max_length=20)
    order_date = DateField()
    cust_po = CharField(max_length=64)
    ship_no = CharField(max_length=20)
    ship_date = DateField()
    width = DecimalField(max_digits=7, decimal_places=4)
    length = DecimalField(max_digits=7, decimal_places=4)
    walls = PositiveSmallIntegerField()

    # Foreign Keys
    customer = ForeignKey(Customer, on_delete=RESTRICT)
    flute = ForeignKey(Flute, on_delete=RESTRICT)
    corrugator = ForeignKey(Corrugator, on_delete=RESTRICT)
    test_code = ForeignKey(OrderTestCode, on_delete=RESTRICT)
    spec_code = ForeignKey(SpecialInstructionCode, on_delete=RESTRICT)

    def get_order_no(self):
        logger.debug(message=f"Returning self.order_no {self.order_no}")
        return self.order_no

    def get_customer_name(self):
        logger.debug(message=f"Returning self.customer.get_name() {self.customer.get_name()}")
        return self.customer.get_name()

    def get_customer_no(self):
        logger.debug(message=f"Returning self.customer.get_cust_no() {self.customer.get_cust_no()}")
        return self.customer.get_cust_no()

    def get_plant_code(self):
        logger.debug(message=f"Returning plant.code {self.plant.code}")
        return self.plant.code

    def get_order_test_code(self):
        logger.debug(message=f"Returning self.test_code.code {self.test_code.code}")
        return self.test_code.code

    def get_spec_code(self):
        logger.debug(message=f"Returning self.spec_code.code {self.spec_code.code}")
        return self.spec_code.code

    def get_plant_desc(self):
        logger.debug(message=f"Returning plant.desc {self.plant.desc}")
        return self.plant.desc

    def get_flute_code(self):
        logger.debug(message=f"Returning self.flute.code {self.flute.code}")
        return self.flute.code

    def get_flute_desc(self):
        logger.debug(message=f"Returning self.flute.desc {self.flute.desc}")
        return self.flute.desc

    def get_corrugator_id(self):
        logger.debug(message=f"Returning self.corrugator.get_id() {self.corrugator.get_id()}")
        return self.corrugator.get_id()

    def get_corrugator_name(self):
        logger.debug(message=f"Returning self.corrugator.get_name() {self.corrugator.get_name()}")
        return self.corrugator.get_name()

class LithoPaper(StandardModel):
    litho_uuid = CharField(max_length=11, unique=True)
    # Example 1: LL1234567MS
    # Example 2: LL3334444MC
    litho_pt = IntegerField(default=0)

    def get_litho_point(self):
        return litho_pt.code
