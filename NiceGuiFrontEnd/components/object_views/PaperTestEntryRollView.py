""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app

class PaperTestEntryRollView(DjangoWebOLV):
  """
  subclass of niceview, data and columns initialized as shown
  """
  def __init__(self):
    self.default_columns = {
                        "roll_no": {'label':"Roll #",'type':str,'default':0},
                        "grade": {'label':"Grade",'type':int,'default':0},
                        "inv_tcode": {'label':'Type','type':str,'default':0},
                        "actual_width": {'label':'Width','type':float,'default':0},
                        "rec_date": {'label': 'Received', 'type': str, 'default': 0},
    }
    self.init_columns = {}
    for col, options in self.default_columns.items():
        if options['label'] in app.storage.user.get("preferences")['page_settings']['paper_test_entry']['roll_view_columns']:
            self.init_columns[col] = options
    super().__init__(column_defs=self.init_columns, max_page_size=15)

