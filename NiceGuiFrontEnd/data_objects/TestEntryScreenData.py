from nicegui import ui


class TestEntryScreenData:
    display_dict = {}

    def __init__(self):
        self.plant = ""
        self.selected_test = {}
        self.selected_row = {}

        for attr in self.display_dict.keys():
            self.selected_row[f"{attr}"] = ''

    def update_selected_panel(self, row=None):
        # ui.notify(f"update_selected_panel row={row}")
        if row is not None:
            for attr in row:
                self.selected_row[f'{attr}'] = row[attr]
        else:
            for attr in self.selected_row.keys():
                self.selected_row[f'{attr}'] = ""


    def update_selected_test(self, test=None):
        if test is not None:
            for attr in test:
                self.selected_test[f'{attr}'] = test[attr]
        else:
            self.selected_test = {}


class PaperTestEntryScreenData(TestEntryScreenData):
    def __init__(self):
        self.roll_no = ""
        self.litho_uuid= ""
        # TODO - Determine which fields are appropriate to add to the database
        self.display_dict = {"roll_no": "Roll Number",
                             "vroll_no": "Vendor Number",
                             "vendor_name": "Vendor Name",
                             "grade": "Grade",
                             "inv_tcode": "Type",
                             "actual_width": "Width",
                             "rec_date": "Received Date",
                             # Not really needed
                             "talley_id": "Talley ID",
                             "vendor_code": "Vendor Code",
                             "orig_weight": "Original Weight",
                             "orig_linear_f": "Original Lineal FT",
                             "orig_msf": "Original MSF",
                             "mill": "Mill",
                             "moisture": "Moisture",
                             "inv_pcode": "Plant",
                             # Omit if not supervisor
                             "cost_by_ton": "Cost per ton",
                             "cost_by_msf": "Cost per MSF",
                             # Litho Paper Roll Selected Panel
                             "litho_uuid": "Litho UUID",
                             "litho_pt": "Litho Point",
                             "created_at": "Created At",
                             "plant_code": "Plant Code",
                             }
        super().__init__()


class CombinedTestEntryScreenData(TestEntryScreenData):
    def __init__(self):
        # TODO - Determine which fields are appropriate to add to the database
        self.display_dict = {"order_no": "Order Number",
                             "plant_code": "Plant Code",
                             "customer_name": "Customer Name",
                             "cust_no": "Customer Number",
                             "ship_no": "Ship To",
                             "order_date": "Order Date",
                             "test_code": "Test",
                             "corru_id": "Corrugator ID",
                             "corrugator_corru_name": "Corrugator Name",
                             "ship_date": "Ship Date",
                             "cust_po": "Customer PO",
                             "spec_code": "Spec Code",
                             "flute_code": "Flute Code",
                             "flute_flute_desc": "Flute Description",
                             "length": "Length",
                             "width": "Width",
                             "qty": "Quantity",
                             "number_of_walls": "Walls",
                             }
        self.order_no = ""
        super().__init__()
