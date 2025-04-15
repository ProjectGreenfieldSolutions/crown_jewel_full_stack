""" base class for object viewing """
from nicegui import ui, run
from copy import deepcopy
import asyncio
import re

from local.Logging import Logger

logger = Logger(__file__)

# JavaScript function to format numbers to 4 decimal places
float_value_formatter = """
function(params) {
    return parseFloat(params.value).toFixed(4);
}
"""


class DjangoWebOLV(ui.aggrid):
    """
    Simple Object viewer using nicegui's aggrid widget
    This widget requires a container to render properly
    dynamic table setup with quick filtering, updating and exporting
    :param: objs to display
    :param: column_defs dict of fields and labels
    """

    def __init__(self, objs=None, column_defs=None, max_page_size=10, selectable=True, enable_checkboxes=True):
        self.screen_name = ""
        self.column_defs = column_defs if column_defs is not None else []
        self.objs = objs if objs is not None else []
        self.show_checks = enable_checkboxes

        params = {
            'columnDefs': self.return_defined_column_defs() if column_defs is not None else None,
            'rowData': objs if objs is not None else []}
        # todo: investigate this
        if selectable:
            params['rowSelection'] = 'single'
        params['pagination'] = 'true'
        params['paginationPageSize'] = max_page_size
        super().__init__(params)
        with self:
            self.style('flex: 1; width: 100%; overflow: auto;')

    def getColumnLabel(self, k):
        return self.column_defs[k]['label'] if 'label' in self.column_defs[k].keys() else self.column_defs.keys()[k]

    def return_defined_column_defs(self):
        """
        function for creating a list of column headers
        :return: list of dictionaries [{},{}]
        """
        # Enable to allow users to select individual rows for exporting
        return_list = [{'checkboxSelection': self.show_checks, 'sortable': True, 'minWidth': 10, 'maxWidth': 40}]
        x = {}
        for k in self.column_defs.keys():
            if self.column_defs[k]['type'] == float:
                return_list.append({'field': k, 'headerName': self.getColumnLabel(k), 'flex': 1, 'resizable': True,
                                    'filter': 'agNumberColumnFilter', 'floatingFilter': True,
                                    "valueFormatter": 'value.toFixed(4)'})
            elif self.column_defs[k]['type'] == int:
                return_list.append({'field': k, 'headerName': self.getColumnLabel(k), 'flex': 1, 'resizable': True,
                                    'filter': 'agNumberColumnFilter', 'floatingFilter': True})
            elif self.column_defs[k]['type'] == str:
                return_list.append({'field': k, 'headerName': self.getColumnLabel(k), 'flex': 1, 'resizable': True,
                                    'filter': 'agTextColumnFilter', 'floatingFilter': True})
            else:
                return_list.append({'field': k, 'headerName': self.getColumnLabel(k), 'flex': 1, 'resizable': True,
                                    'filter': 'agTextColumnFilter', 'floatingFilter': True})
            if self.column_defs[k].__contains__('default'):
                x[k] = self.column_defs[k]['default']

        return return_list

    def generate_row_data(self):
        """
        returns row data from assigned objects
        :return: [{},{}]
        """
        return [obj.__dict__ for obj in self.objs]

    def export_all_data_to_csv(self, location="reports/data.csv", filename="csv_download.csv"):
        """
        export the grid data to a csv at the target location
        :param location: str
        """
        import csv

        # Escape if the dataset is empty
        objects = self.objs
        if not objects:
            return

        if self.screen_name == "combined_tests":
            new_results = []
            previous_order_no = objects[0]["order_no"]

            for index, row in enumerate(objects):
                try:
                    if row["IGNORE"]:
                        continue
                except KeyError:
                    pass

                # Get the current combined board test type
                current_test_type = row["combined_test_type"].lower().replace(" ", "_")

                # New order detected
                if previous_order_no != row["order_no"] or index == 0:

                    temp_row = {}
                    for column in ["id", "created_at", "order_no", "order_corrugator_name", "order_customer_name", "order_test_code", "order_flute_desc", "order_ship_date"]:
                        temp_row[column] = deepcopy(row[column])

                    # Loop through all layers
                    for layer in objects[-1]["combined_test_layers"]:
                        converted_layer = objects[-1]['layer_id_mapping'][layer]
                        # Correlate the linked ID records to appropriate information
                        if not layer == "l1":
                            temp_row[f"{layer}_corrchoice#"]     = row[f"combined_roll_{converted_layer}"]
                            temp_row[f"{layer}_roll_vendor"]     = row[f"l{converted_layer}_roll_vendor"]
                            temp_row[f"{layer}_roll_grade"]      = row[f"l{converted_layer}_roll_grade"]
                            temp_row[f"{layer}_roll_paper_type"] = row[f"l{converted_layer}_roll_paper_type"].upper()
                        else:
                            if row["combined_roll_1"]:
                                temp_row[f"{layer}_corrchoice#"]     = row[f"combined_roll_1"]
                                temp_row[f"{layer}_roll_vendor"]     = row[f"l{converted_layer}_roll_vendor"]
                                temp_row[f"{layer}_roll_grade"]      = row[f"l{converted_layer}_roll_grade"]
                                temp_row[f"{layer}_roll_paper_type"] = row[f"l{converted_layer}_roll_paper_type"].upper()
                            else:
                                temp_row[f"{layer}_corrchoice#"]     = "LITHO"
                                temp_row[f"{layer}_roll_vendor"]     = "LITHO"
                                # re below does... Removal of all alphabetic characters from the string
                                try:
                                    temp_row[f"{layer}_roll_grade"]      = re.sub(r'[a-zA-Z]', '', row[f"combined_litho_1"])
                                except:
                                    logger.info(message=f"combined litho #1 is empty")
                                temp_row[f"{layer}_roll_paper_type"] = "PT"

                    for test_types in objects[-1]["combined_test_types"]:
                        temp_row[test_types] = None

                    temp_row[current_test_type] = row["test_value"]
                    temp_row["combined_test_reason"] = row["combined_test_reason"]
                    temp_row["author"] = row["test_author"]
                    temp_row["plant"] = row["plant_desc"]

                    new_results.append(temp_row)
                else:
                    # Existing order no
                    for temp in new_results:
                        if not temp["order_no"] == previous_order_no:
                            continue
                        else:
                            temp[current_test_type] = row["test_value"]
                            break

                # Update previous order for the next loop
                previous_order_no = row["order_no"]

            objects = deepcopy(new_results)

        with open(location, 'w+', ) as csvfile:
            writer = csv.writer(csvfile)
            for idx, row in enumerate(objects):
                if idx == 0:
                    writer.writerow([key.replace("_", " ").upper() for key in row.keys()])
                writer.writerow([value for value in row.values()])

    async def export_data_non_blocking(self, location="reports/data.xlsx", filename="excel_file", format='xlsx'):
        # Async function to handle non-blocking export
        if not self.objs:
            ui.notify("Selected table is empty!")
            return

        ui.notify(f"Building export file for format {format}")
        if format == 'xlsx':
            # Run data export (saving the file) in a background thread
            await run.io_bound(self.export_all_data_to_excel, location)
        if format == 'csv':
            await run.io_bound(self.export_all_data_to_csv, location)

        # Initiate the download on the main thread after saving completes
        ui.download(location, filename)
        ui.notify(f"File '{filename}' downloading")

    def export_all_data_to_excel(self, location="reports/data.xlsx"):
        """
        Export the grid data to an Excel file at the target location
        :param location: str
        """
        import xlsxwriter
        objects = deepcopy(self.objs)

        # Escape if the dataset is empty
        if not objects:
            return

        # Build the worksheet
        wb = xlsxwriter.Workbook(location)
        ws = wb.add_worksheet()

        # logger.info(objects)
        if self.screen_name == "combined_tests":
            new_results = []
            previous_order_no = objects[0]["order_no"]

            for index, row in enumerate(objects):
                try:
                    if row["IGNORE"]:
                        continue
                except KeyError:
                    pass

                # Get the current combined board test type
                current_test_type = row["combined_test_type"].lower().replace(" ", "_")

                # New order detected
                if previous_order_no != row["order_no"] or index == 0:

                    temp_row = {}
                    for column in ["id", "created_at", "order_no", "order_corrugator_name", "order_customer_name", "order_test_code", "order_flute_desc", "order_ship_date"]:
                        temp_row[column] = deepcopy(row[column])

                    # Loop through all layers
                    for layer in objects[-1]["combined_test_layers"]:
                        converted_layer = objects[-1]['layer_id_mapping'][layer]
                        # Correlate the linked ID records to appropriate information
                        if not layer == "l1":
                            temp_row[f"{layer}_corrchoice#"]     = row[f"combined_roll_{converted_layer}"]
                            temp_row[f"{layer}_roll_vendor"]     = row[f"l{converted_layer}_roll_vendor"]
                            temp_row[f"{layer}_roll_grade"]      = row[f"l{converted_layer}_roll_grade"]
                            if row[f"l{converted_layer}_roll_paper_type"]:
                                temp_row[f"{layer}_roll_paper_type"] = row[f"l{converted_layer}_roll_paper_type"].upper()
                            else:
                                temp_row[f"{layer}_roll_paper_type"] = None

                        else:
                            if row["combined_roll_1"]:
                                temp_row[f"{layer}_corrchoice#"]     = row[f"combined_roll_1"]
                                temp_row[f"{layer}_roll_vendor"]     = row[f"l{converted_layer}_roll_vendor"]
                                temp_row[f"{layer}_roll_grade"]      = row[f"l{converted_layer}_roll_grade"]
                                if row[f"l{converted_layer}_roll_paper_type"]:
                                    temp_row[f"{layer}_roll_paper_type"] = row[f"l{converted_layer}_roll_paper_type"].upper()
                                else:
                                    temp_row[f"{layer}_roll_paper_type"] = None
                            else:
                                temp_row[f"{layer}_corrchoice#"]     = "LITHO"
                                temp_row[f"{layer}_roll_vendor"]     = "LITHO"
                                # re below does... Removal of all alphabetic characters from the string
                                try:
                                    temp_row[f"{layer}_roll_grade"]      = re.sub(r'[a-zA-Z]', '', row[f"combined_litho_1"])
                                except:
                                    logger.info(message=f"combined litho #1 is empty")
                                temp_row[f"{layer}_roll_paper_type"] = "PT"

                    for test_types in objects[-1]["combined_test_types"]:
                        temp_row[test_types] = None

                    temp_row[current_test_type] = row["test_value"]
                    temp_row["combined_test_reason"] = row["combined_test_reason"]
                    temp_row["author"] = row["test_author"]
                    temp_row["plant"] = row["plant_desc"]

                    new_results.append(temp_row)
                else:
                    # Existing order no
                    for temp in new_results:
                        if not temp["order_no"] == previous_order_no:
                            continue
                        else:
                            temp[current_test_type] = row["test_value"]
                            break

                # Update previous order for the next loop
                previous_order_no = row["order_no"]

            objects = deepcopy(new_results)
        elif self.screen_name == "paper_tests":
            new_results = []

            for index, row in enumerate(objects):
                try:
                    if row["IGNORE"]:
                        continue
                except KeyError:
                    pass

                temp_row = {}

                temp_row = deepcopy(row)

                if not temp_row["roll_no"]:
                    temp_row["roll_no"] = deepcopy(temp_row["litho_uuid"])
                    temp_row["roll_tally_id"] = f"{deepcopy(temp_row['litho_pt'])}" + "PT"

                del temp_row["litho_uuid"]
                del temp_row["litho_pt"]
                new_results.append(temp_row)

            objects = deepcopy(new_results)

        # Build the header
        headers = [attr.replace("_", " ").upper() for attr in objects[0]]
        ws.write_row(0, 0, headers)

        # Build the rows
        for idx, row_obj in enumerate(objects, start=1):
            ws.write_row(idx, 0, [row_obj[key] for key in row_obj])

        # Complete the file
        wb.close()

    async def update_data(self, objs):
        """
        update the view with new data
        :param objs to display
        """
        # Clear list of objects
        self.objs = []

        # Clear table contents
        self.clear()

        if not objs:
            # Blank out the screen if query failed
            self.options['rowData'] = self.objs
            with self:
                ui.notify("No records found!")
            return

        # Assign fetched records to object's "objs"
        self.objs = objs

        # Variables used to hold the paper test screen display data, which is different than
        # the self.objs (aka django returned objects)
        displayed_data = []
        template_displayed_row = {}
        displayed_row = []
        total = 0.0

        # Craft a template dictionary to deepcopy this, rather than something much larger
        for key in self.objs[0].keys():
            template_displayed_row[key] = ""

        if self.screen_name == "paper_tests":
            # Loop through each row
            for row in objs:
                # Loop through each column of a row
                for column_header, value in row.items():
                    # If count is greater than one, we have a valid entry to display
                    if "count" in column_header:
                        if not row[column_header]:
                            # Is None, backends way of saying its zero
                            continue

                        if int(row[column_header]) >= 1:
                            # Assign needed values here now
                            displayed_row = deepcopy(template_displayed_row)
                            displayed_row["created_at"] = row["created_at"]
                            if not row["roll_no"]:
                                displayed_row["roll_no"] = row["litho_uuid"]
                                displayed_row["roll_grade"] = f"{row['litho_pt']}" + "PT"
                            else:
                                displayed_row["roll_no"] = row["roll_no"]
                                displayed_row["roll_grade"] = row["roll_grade"]
                                displayed_row["roll_width"] = row["roll_width"]
                                displayed_row["roll_type"] = row["roll_type"]

                            displayed_row["test_type"] = column_header[:-6].replace("_", " ").title()

                    if "values" in column_header:
                        # Aggregate the average of values here
                        if row[column_header]:
                            if "," in row[column_header]:
                                values = [value for value in row[column_header].split(",")]
                                for value in values:
                                    total += round(float(value), 4)
                                displayed_row["test_value"] = total / float(len(values))
                                # Reset total counter
                                total = 0.0
                            else:
                                displayed_row["test_value"] = row[column_header]

                            displayed_row["test_value"] = f"{float(displayed_row['test_value']):.4f}"
                            displayed_data.append(displayed_row)
        elif self.screen_name == "combined_tests":
            for row in objs:
                try:
                    if row["IGNORE"]:
                        continue
                except KeyError:
                    pass

                # Copy backend row record
                displayed_row = deepcopy(row)

                # Move the name of existing database fields to table column names
                displayed_row["test"] = row["order_test_code"]
                displayed_row["flute"] = row["order_flute_desc"]
                displayed_row["test_type"] = row["combined_test_type"]
                displayed_row["test_reason"] = row["combined_test_reason"]
                displayed_row["author"] = row["test_author"]
                displayed_row["plant"] = row["plant_desc"]

                # Append new row information to table
                displayed_data.append(deepcopy(displayed_row))
        else:
            # Not combined board tests nor paper tests
            # Shouldn't occur but it might in the future (02/06/2025)
            displayed_data = self.objs

        self.options['rowData'] = displayed_data
        with self:
            ui.notify("Table records collected!")

    def add_objects(self, objs):
        """
        update the view with new data
        :param objs to display
        """
        self.clear()
        for obj in objs:
            self.objs.append(obj)
        self.options['rowData'] = self.objs

    def add_object(self, obj):
        """
        update the view with new data
        :param objs to display
        """
        self.clear()
        self.objs.append(obj)
        self.options['rowData'] = self.objs

    def remove_object(self, obj):
        """
        update the view with new data
        :param objs to display
        """
        self.clear()
        self.objs.remove(obj)
        self.options['rowData'] = self.objs

    async def export_selected_rows(self, location="data.csv"):
        """
        export selected rows from the data table to target csv
        :param location: str
        """
        if not location or not location.__contains__(".csv"):
            return ui.notify('Please correct the filepath to a .csv')

        import csv
        selections = await self.get_selected_rows()
        with open(location, 'w+', ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(selections[0].keys())
            for obj in selections:
                writer.writerow(obj.values())

        ui.notify(f"Saved selected to: {location}")

    async def export_selected_rows_excel(self, location="data.xlsx"):
        """
        Export selected rows from the data table to an Excel file at the target location
        :param location: str
        """
        from openpyxl import Workbook
        # Get selected rows asynchronously
        objects = await self.get_selected_rows()

        if len(objects) > 0:
            # Create a new workbook and select the active sheet
            wb = Workbook()
            ws = wb.active

            # Extract headers from the first object
            headers = [attr for attr in dir(objects[0]) if
                       not attr.startswith('__') and not callable(getattr(objects[0], attr))]
            ws.append(headers)  # Add headers to the first row

            # Write data rows
            for obj in objects:
                row = [getattr(obj, attr) for attr in headers]
                ws.append(row)

            # Save the workbook to the specified location
            wb.save(location)
            ui.notify(f"Saved selected to: {location}")


if __name__ == '__main__':
    # Example usage:
    init_data = [{"id": 0, "roll_no": "0", "roll_grade": "0", "roll_type": "--", "roll_width": 0.00, "test_type": "---",
                  "average": 00.0}]
    data = [
        {"id": 0, "roll_no": "foo", "roll_grade": "26", "roll_type": "RCL", "roll_width": 98.00, "test_type": "Caliper",
         "average": 48.6},
        {"id": 1, "roll_no": "569966MS", "roll_grade": "26", "roll_type": "RCL", "roll_width": 98.00,
         "test_type": "Ring Crush CD", "average": 0.121},
        {"id": 2, "roll_no": "569966MS", "roll_grade": "26", "roll_type": "RCL", "roll_width": 98.00,
         "test_type": "Porosity", "average": 61.9},
        {"id": 3, "roll_no": "569966MS", "roll_grade": "26", "roll_type": "RCL", "roll_width": 98.00,
         "test_type": "Basis Weight", "average": 52.7},
    ]

    with ui.row().style('height: 90vh; width: 100%; display: flex; flex-direction: column;'):
        nv = DjangoWebOLV(init_data, column_defs={'id': 'foo'})

    asyncio.create_task(nv.update_data(data))
    # Run the UI
    ui.run(native=True, reload=False, window_size=(2048, 1080))
