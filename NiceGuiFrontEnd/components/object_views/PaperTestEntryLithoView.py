""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app

class PaperTestEntryLithoView(DjangoWebOLV):
  """
  subclass of niceview, data and columns initialized as shown
  """
  def __init__(self):
    self.default_columns = {
                        "litho_uuid": {'label':"Litho UUID",'type':str,'default':0},
                        "litho_pt": {'label':"Litho Point",'type':int,'default':0},
                        "created_at": {'label': 'Created At', 'type': str, 'default': 0},
                        "plant_code": {'label': 'Plant Code', 'type': str, 'default': 0},
    }
    self.init_columns = {}
    for col, options in self.default_columns.items():
        if options['label'] in app.storage.user.get("preferences")['page_settings']['paper_test_entry']['litho_paper_view_columns']:
            self.init_columns[col] = options
    super().__init__(column_defs=self.init_columns, max_page_size=15)

