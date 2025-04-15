from django.conf import settings
from django.db.models import AutoField, CharField, DateField, DateTimeField, DecimalField, FloatField, IntegerField, PositiveSmallIntegerField
from django.db.models import ForeignKey, Model
from django.db.models import CASCADE, RESTRICT
from local.Logging import Logger
logger = Logger(__file__)

class Plant(Model):
    id = AutoField(primary_key=True)
    code = CharField(max_length=6)
    desc = CharField(max_length=25)

    # History fields
    created_at = DateTimeField(auto_now_add=True)
    last_updated = DateTimeField(auto_now=True)

    def get_code(self):
        logger.debug(message=f"Returning self.code {self.code}")
        return self.code

    def get_desc(self):
        logger.debug(message=f"Returning self.desc {self.desc}")
        return self.desc

class StandardModel(Model):
    class Meta:
        abstract = True

    id = AutoField(primary_key=True)

    # Foreign Keys
    plant = ForeignKey(Plant, on_delete=RESTRICT)

    # History fields
    created_at = DateTimeField(auto_now_add=True)
    last_updated = DateTimeField(auto_now=True)

class KeyValuePairModel(StandardModel):
    class Meta:
        abstract = True
        unique_together = ("code", "plant")

    code = CharField(max_length=20)
    desc = CharField(max_length=100, blank=True)

    def get_plant_code(self):
        logger.debug(message=f"Returning plant.code {self.plant.code}")
        return self.plant.code

    def get_plant_desc(self):
        logger.debug(message=f"Returning plant.desc {self.plant.desc}")
        return self.plant.desc

    def get_code(self):
        logger.debug(message=f"Returning self.code {self.code}")
        return self.code

    def get_desc(self):
        if self.desc != "":
            logger.debug(message=f"self.desc != ''")
            logger.debug(message=f"Returning self.desc {self.desc}")
            return self.desc
        else:
            logger.debug(message=f"self.code == ''")
            logger.debug(message=f"Returning self.code {self.code}")
            return self.code
