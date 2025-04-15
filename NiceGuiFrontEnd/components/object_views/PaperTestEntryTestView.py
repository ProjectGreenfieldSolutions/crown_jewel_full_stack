""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app

class PaperTestEntryTestView(DjangoWebOLV):
  """
  subclass of niceview, data and columns initialized as shown
  """
  def __init__(self):
    self.default_columns = {
                        "roll_no": {'label':"Roll #",'type':str},
                        "test_type": {'label': "Test Type", "type": str},
                        "test_reason": {'label':"Test Reason",'type':str},
                        "test_position": {'label':"Test Position",'type':str},
                        "test_value": {'label':'Test Value','type':float},
                         }
    self.init_columns = {}
    for col, options in self.default_columns.items():
        if options['label'] in app.storage.user.get("preferences")['page_settings']['paper_test_entry']['test_view_columns']:
            self.init_columns[col] = options
    super().__init__(column_defs=self.init_columns, max_page_size=15)

