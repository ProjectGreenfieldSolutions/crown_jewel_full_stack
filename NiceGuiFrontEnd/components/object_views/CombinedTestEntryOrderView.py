""" object view for the paper test screen """
from components.object_views.DjangoWebOLV import DjangoWebOLV
from nicegui import app

class CombinedTestEntryOrderView(DjangoWebOLV):
  """
  subclass of niceview, data and columns initialized as shown
  {'plant_code': 'MS', 'order_no': '456456', 'cust_no': '1130', 'customer_name': 'Grand Rapids-Opus Pkg', 'cust_po': '39951-27',
'ship_no': '0', 'order_date': '02/01/19', 'ship_date': '02/06/19', 'qty': '300',
 'test_code': '32', 'flute_code': '1',
 'flute_flute_desc': 'C', 'spec_code': '1', 'width': '35.1416', 'length': '81.0616', 'corru_id': 'm1',
  'corrugator_corru_name': 'MPM Line 1 (BHS)', 'number_of_walls': '1'}
  """
  def __init__(self):
    self.default_columns = {
                        # these are available in preferences
                        "order_no": {'label': "Order No", 'type': str},
                        "customer_name": {'label': 'Customer Name', 'type': str},
                        "qty": {'label': 'Quantity', 'type': int},
                        "width": {'label': "Width", 'type': float},
                        "length": {'label': 'Length', 'type': float},
                        "plant_code": {'label':"Plant Code",'type':str},
                        # these are not but can be added to be enabled
                        "cust_no": {'label':'Customer Number','type':str},
                        "cust_po": {'label': "Order P.O.", 'type': str, },
                        "ship_no": {'label':"Ship Number",'type':str},
                        "order_date": {'label':'Order Date','type':str},
                        "ship_date": {'label':'Ship Date','type':str},
                        "test_code": {'label':"Test Code",'type':str},
                        "flute_code": {'label':'Customer Code','type':str},
                        "flute_flute_desc": {'label':'Flute Description','type':str},
                        "spec_code": {'label': "Spec Code", 'type': str, },
                        "corru_id": {'label':'Corrugator ID','type':str},
                        "corrugator_corru_name": {'label':'Corrugator Name','type':str},
                        "number_of_walls": {'label':'Number of Walls','type':str},

    }
    self.init_columns = {}
    for col, options in self.default_columns.items():
        if options['label'] in app.storage.user.get("preferences")['page_settings']['combined_test_entry']['order_view_cols']:
            self.init_columns[col] = options
    super().__init__(column_defs=self.init_columns, max_page_size=15)
    # unused values


