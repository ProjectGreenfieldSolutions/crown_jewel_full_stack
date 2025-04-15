from nicegui import ui, app

from pages.NiceKTCPage import NiceKTCPage


class ModificationScreenManagerPage(NiceKTCPage):
    def __init__(self):
        super().__init__()
        with self.classes('w-full h-full'):
            self.selected_table = ""
            self.add_update_button_text = "Add new record"
            self.add_update_button_color = "green"

            self.default_table_data = {
                "title": "Nothing Selected",
                "columns": [
                    {"name": "code", "label": "Code", "field": "code"},
                    {"name": "desc", "label": "Description", "field": "desc"},
                ],
                "rows": [],
            }

            self.table_data = {

            }

            self.default_form_data = {
                "code": None,
                "desc": None,
                "table": None,
            }

            self.form_data = {

            }

            self.default_accounts_table_data = {
                "title": "Accounts",
                "columns": [
                    {"name": "username", "label": "Username", "field": "username"},
                    {"name": "active", "label": "Is Active?", "field": "is_active"},
                    {"name": "supervisor", "label": "Is Supervisor?", "field": "is_supervisor"},
                    {"name": "admin", "label": "Is Admin?", "field": "is_admin"},
                ],
                "rows": [],
            }

            self.accounts_table_data = {

            }

            self.default_accounts_form_data = {
                "table": None,
                "username": app.storage.user.get("username"),
                "is_active": True,
                "is_supervisor": False,
                "is_admin": False,
            }

            self.accounts_form_data = {

            }

            self.list_of_tables = ["lithos", "paper_test_reasons", "paper_test_positions", "paper_test_types",
                                   "combined_board_test_reasons", "combined_board_test_layers", "combined_board_test_types"]

            # TODO - Include way for non-ktc users to see this
            if app.storage.user.get("username") == "ktc":
                self.list_of_tables.append("accounts")

            self.dict_of_tables = {"": ""}

            self.startup_procedure()

    def check_if_existing(self, code_value:str):
        all_row_values = self.table_data['rows']
        for row in all_row_values:
            if code_value == row["code"]:
                self.add_update_button_text = "Update existing record"
                self.add_update_button_color = "orange"
                self.create_add_update_button.refresh()
                return

        self.add_update_button_text = "Add new record"
        self.add_update_button_color = "green"
        self.create_add_update_button.refresh()

    def build_dict_of_tables(self):
        for table in self.list_of_tables:
            self.dict_of_tables[table] = self.pretty_table_name(table)

    def startup_procedure(self):
        self.reset_everything()
        self.build_dict_of_tables()
        with ui.grid(columns=2).classes("w-full"):
            self.create_table_selection()
            self.create_table_clear()
            self.create_table()
            self.create_form()

    def create_table_selection(self):
        return ui.select(
            label="Selected Table",
            options=self.dict_of_tables,
            value=""
        ).bind_value(self, "selected_table").classes("w-full").on_value_change(self.update_table)

    def create_table_clear(self):
        with ui.card():
            ui.label("Reset the screen")
            ui.button(f"Start over", on_click=lambda: self.reset_everything()).classes("w-full").props("color='red'")

    @ui.refreshable
    def create_add_update_button(self):
        return ui.button(f"{self.add_update_button_text}", on_click=lambda: self.update_table(modify=True)).props(
            f"color='{self.add_update_button_color}'")

    @ui.refreshable
    def create_table(self):
        with ui.card():
            ui.table(title=self.table_data["title"],
                     columns=self.table_data["columns"],
                     rows=self.table_data["rows"]
                     ).classes("w-full")

    @ui.refreshable
    def create_form(self):
        with ui.card().classes("w-full"):
            ui.label(f"Form entry for table {self.pretty_table_name(self.table_data['title'])}")
            if not self.table_data["title"] == "Accounts":
                with ui.grid(columns=2).classes("w-full"):
                    ui.input(label="Code", placeholder="code_must_use_underscores_for_spaces",
                             on_change=lambda: self.check_if_existing(self.form_data["code"])).bind_value(
                        self.form_data,
                        "code")
                    ui.input(label="Description", placeholder="Descriptions can be anything you want").bind_value(
                        self.form_data,
                        "desc")
                    self.create_add_update_button()
            else:
                with ui.grid(columns=4).classes("w-full"):
                    ui.input(label="Username", placeholder="smithj").bind_value(self.accounts_form_data, "username")
                    ui.select(label="is_active", options={False: "False", True: "True"}).bind_value(
                        self.accounts_form_data, "is_active")
                    ui.select(label="is_supervisor", options={False: "False", True: "True"}).bind_value(
                        self.accounts_form_data, "is_supervisor")
                    ui.select(label="is_admin", options={False: "False", True: "True"}).bind_value(
                        self.accounts_form_data, "is_admin")
                with ui.grid(columns=2).classes("w-full"):
                    ui.button("Update user", on_click=lambda: self.update_table(modify=True)).props("color='blue'")

    def reset_everything(self):
        self.selected_table = ""
        self.form_data = self.default_form_data.copy()
        self.accounts_form_data = self.default_accounts_form_data.copy()
        self.table_data = self.default_table_data.copy()
        self.accounts_form_data = self.default_accounts_form_data.copy()
        self.create_table.refresh()
        self.create_form.refresh()

    def rebuild_components(self):
        rows = []
        if not self.selected_table == "accounts" and self.selected_table:
            # Records from backend
            records = app.connection_manager.GetConnection(endpoint="/util",
                                                           payload={"action": f"{self.selected_table}",
                                                                    "plant_code": app.storage.user.get("plant")})

            if records:
                # Reset the table/form data
                self.table_data = self.default_table_data.copy()
                self.form_data = self.default_form_data.copy()

                # Assign title
                self.table_data["title"] = self.pretty_table_name(self.selected_table)

                # Assign table to form payload
                self.form_data["table"] = self.selected_table

                # # Actual record values
                # records = records["records"]

                # Assign row records
                for key, value in records.items():
                    row_dict = {"code": key, "desc": value}
                    rows.append(row_dict)

            # Backend status message
            # ui.notify("")

        elif self.selected_table == "accounts" and self.selected_table:
            # Records from backend
            records = app.connection_manager.GetConnection(endpoint="/get_accounts",
                                                           payload={"username": app.storage.user.get("username")})

            if records["status"] == "success":
                # Reset the table/form data
                self.table_data = self.default_accounts_table_data.copy()
                self.accounts_form_data = self.default_accounts_form_data.copy()

                # Assign title
                self.table_data["title"] = self.pretty_table_name(self.selected_table)
                self.accounts_form_data["table"] = self.selected_table

                for account in records["records"]:
                    row_dict = {"username": account["username"], "is_active": account["is_active"],
                                "is_supervisor": account["is_supervisor"], "is_admin": account["is_admin"], }
                    rows.append(row_dict)
            elif records["status"] == "failure":
                self.reset_everything()
            ui.notify(records["message"])
        else:
            app.logger.critical("ERROR - No table selected")

        # Assign the rows for the table
        self.table_data["rows"] = rows
        self.create_table.refresh()
        self.create_form.refresh()

    def update_table(self, modify=False):
        if self.selected_table:
            ui.notify(f"Updating table information... ({self.selected_table})")
        else:
            ui.notify("Clearing table information...")

        if modify:
            if self.selected_table == "accounts":
                results = app.connection_manager.GetConnection(endpoint="/update_accounts",
                                                               payload=self.accounts_form_data)
            else:
                results = app.connection_manager.GetConnection(endpoint="/modify_entry", payload=self.form_data)

            if results:
                if results["status"]:
                    ui.notify(results["status"] + " : " + results["message"])
                else:
                    ui.notify("Update failed!")

        # Refresh the table
        self.rebuild_components()
        self.create_table.refresh()
        self.create_form.refresh()

    def assign_selected_table(self, table_name):
        self.selected_table = table_name
        self.rebuild_components()

    @staticmethod
    def pretty_table_name(name: str):
        try:
            return name.replace("_", " ").title()
        except Exception as e:
            app.logger.warning(e)
            return None
