""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app


class RollVerificationView(DjangoWebOLV):
    def __init__(self):
        self.default_columns = {
            "layer": {"label": "Layer", "type": str},
            "roll_no": {"label": "Roll #", "type": str},
            "grade": {"label": "Grade", "type": str},
            "type": {"label": "Type", "type": str},
            "vendor": {"label": "Vendor", "type": str},
        }
        self.init_columns = {}

        # Note: We're using the defaults and never anything else, removed the ability to sub out from preferences
        for col, options in self.default_columns.items():
            self.init_columns[col] = options

        super().__init__(column_defs=self.init_columns, max_page_size=15)
