""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app
from services.Connection import ConnectionManager


class CombinedTestObjectView(DjangoWebOLV):
    """
    subclass of niceview, data and columns initialized as shown
    """

    def __init__(self):
        # TODO: Move to mongo
        self.default_columns = {
            "order_no": {"label": "Order #", "type": str},
            "created_at": {"label": "Created", "type": str},
            "plant": {"label": "Plant", "type": str},
            "author": {"label": "Author", "type": str},
            "test": {"label": "Test", "type": str},
            "flute": {"label": "Flute", "type": str},
            "test_type": {"label": "Test Type", "type": str},
            "test_reason": {"label": "Test Reason", "type": str},
            "test_value": {"label": "Test Value", "type": float}}
        self.init_columns = {}
        for col, options in self.default_columns.items():
            if options['label'] in app.storage.user.get("preferences")['page_settings']['combined_tests'][
                'olv_columns']:
                self.init_columns[col] = options
        super().__init__(column_defs=self.init_columns, max_page_size=27, selectable=False, enable_checkboxes=False)
        self.screen_name = "combined_tests"
        self.user_plant = app.storage.user.get("plant")
        self.connection_manager = ConnectionManager()
