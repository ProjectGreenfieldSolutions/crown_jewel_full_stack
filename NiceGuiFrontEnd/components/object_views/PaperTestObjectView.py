""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app


class PaperTestObjectView(DjangoWebOLV):
    """
    subclass of niceview, data and columns initialized as shown
    """

    def __init__(self):
        # TODO: Move to mongo
        self.default_columns = {"created_at": {"label": "Created", "type": str, "default": 0},
                                "roll_no": {"label": "Roll/Litho #", "type": str, "default": 0},
                                "roll_grade": {"label": "Roll Grade/Litho Point", "type": int, "default": 0},
                                "roll_type": {"label": "Roll Type", "type": str, "default": 0},
                                "roll_width": {"label": "Roll Width", "type": float, "default": 0},
                                "test_type": {"label": "Test Type", "type": str, "default": 0},
                                "test_value": {'label': 'Test Value', 'type': float, 'default': 0}}
        self.init_columns = {}
        for col, options in self.default_columns.items():
            if options['label'] in app.storage.user.get("preferences")['page_settings']['paper_tests']['olv_columns']:
                self.init_columns[col] = options
        super().__init__(column_defs=self.init_columns, max_page_size=27, selectable=False, enable_checkboxes=False)
        self.screen_name = "paper_tests"
        self.user_plant = app.storage.user.get("plant")
