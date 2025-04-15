from nicegui import app, ui
import json

from pages.NiceKTCPage import NiceKTCPage


class PreferencesPage(NiceKTCPage):
    ignored_pages = ["profile", "devlog", "modifications"]

    def __init__(self):
        super().__init__()
        with self.classes('w-full'):
            self.build_pref_tab_panel()
            ui.button("Apply", on_click=self.submit_click).classes("w-full")

    @staticmethod
    def pretty_page_name(page_name: str):
        try:
            return page_name.replace("_", " ").title()
        except Exception as e:
            app.logger.warning(e)
            return None

    def build_user_pref_tab_panel(self):
        with ui.row():
            ui.label("Default Page:")
            page_options = self.page_options()
            self.landing_page_select = ui.select(options=page_options)
            try:
                self.landing_page_select.value = app.storage.user.get("preferences")["landing_page"]
            except:
                self.landing_page_select.value = list(page_options.keys())[0]

    def build_pref_tab_panel(self):
        with ui.row():
            with ui.column():
                # TODO: enable this and hide tab options
                # self.editor_page_select = ui.select(options=page_options)
                with ui.tabs() as tabs:
                    pages = []
                    pages.append(("General", ui.tab("General")))

                    for page_option in self.page_options():
                        if not page_option in self.ignored_pages:
                            pages.append((page_option, ui.tab(self.pretty_page_name(page_option))))

                with ui.tab_panels(tabs, value="General"):  # .bind_value_from(self.editor_page_select, "value"): TODO
                    for page_name, page in pages:
                        with ui.tab_panel(page):
                            ui.label(f"{self.pretty_page_name(page_name)} Settings")
                            with ui.grid(columns=2).classes("w-full"):
                                if page_name == "General":
                                    self.build_user_pref_tab_panel()
                                if page_name == "dashboard":
                                    self.build_dashboard_pref()
                                if page_name == "paper_tests":
                                    self.build_paper_test_pref()
                                if page_name == "combined_tests":
                                    self.build_combined_tests_pref()
                                if page_name == "paper_test_entry":
                                    self.build_paper_test_entry_pref()
                                if page_name == "combined_test_entry":
                                    self.build_combined_test_entry_pref()

    def build_dashboard_pref(self):
        with ui.card():
            ui.label("Show 3D graphs")
            ui.separator()
            self.show_3d = ui.checkbox()
            self.show_3d.value = app.storage.user.get("preferences")["page_settings"]["dashboard"]["show_3d_graphs"]

    def build_paper_test_pref(self):
        with ui.card():
            ui.label("Paper Test Search Options")
            ui.separator()
            paper_filter_options = [x["title"][:-1] for k, x in app.paper_test_default_filters.items()]
            self.paper_test_filter_select = ui.select(options=paper_filter_options, multiple=True)
            self.paper_test_filter_select.value = app.storage.user.get("preferences")["page_settings"]["paper_tests"][
                "filter_attributes"]

        with ui.card():
            ui.label("Paper Test Columns")
            ui.separator()
            self.paper_test_olv_select = ui.select(options=app.paper_test_default_olv_columns, multiple=True)
            self.paper_test_olv_select.value = app.storage.user.get("preferences")["page_settings"]["paper_tests"][
                "olv_columns"]

    def build_combined_tests_pref(self):
        with ui.card():
            ui.label("Combined Search Options")
            ui.separator()
            combined_filter_options = [x["title"][:-1] for k, x in app.combined_test_filter_defaults.items()]
            self.combined_test_filter_select = ui.select(options=combined_filter_options, multiple=True)
            self.combined_test_filter_select.value = \
                app.storage.user.get("preferences")["page_settings"]["combined_tests"][
                    "filter_attributes"]

        with ui.card():
            ui.label("Combined Test Columns")
            ui.separator()
            self.combined_test_olv_select = ui.select(options=app.combined_test_default_olv_columns, multiple=True)
            self.combined_test_olv_select.value = \
            app.storage.user.get("preferences")["page_settings"]["combined_tests"][
                "olv_columns"]

    def build_paper_test_entry_pref(self):
        # Searched roll panel
        with ui.card():
            ui.label("Searched roll table columns to show")
            ui.separator()
            self.roll_view_columns = ui.select(options=app.roll_view_defaults, multiple=True)
            self.roll_view_columns.value = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                "roll_view_columns"] if app.storage.user.get("preferences")["page_settings"][
                "paper_test_entry"] else None
        # Searched litho paper panel
        with ui.card():
            ui.label("Searched litho table columns to show")
            ui.separator()
            self.litho_paper_view_columns = ui.select(options=app.litho_paper_view_defaults, multiple=True)
            self.litho_paper_view_columns.value = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                "litho_paper_view_columns"] if app.storage.user.get("preferences")["page_settings"][
                "paper_test_entry"] else None
        # Selected roll panel
        with ui.card():
            ui.label("Selected roll columns to show")
            ui.separator()
            self.selected_roll_attrs = ui.select(options=app.selected_roll_attrs, multiple=True)
            self.selected_roll_attrs.value = \
                app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                    "selected_roll_attrs"] if app.storage.user.get("preferences")["page_settings"][
                    "paper_test_entry"] else None
        with ui.card():
            ui.label("Selected litho columns to show")
            ui.separator()
            self.selected_litho_attrs = ui.select(options=app.selected_litho_attrs, multiple=True)
            self.selected_litho_attrs.value = \
                app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                    "selected_litho_attrs"] if app.storage.user.get("preferences")["page_settings"][
                    "paper_test_entry"] else None
        # Test entries panel
        with ui.card():
            ui.label(f"Default # of test entries")
            ui.separator()
            self.paper_test_count = ui.number()
            self.paper_test_count.value = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                "test_entry_count"] if app.storage.user.get("preferences")["page_settings"][
                "paper_test_entry"] else 2

        # Test entries panel
        with ui.card():
            ui.label(f"Default test types")
            ui.separator()
            payload = {
                "action": "paper_test_types",
                "plant_code": app.storage.user.get("plant"),
            }
            self.paper_test_types = ui.select(
                options=app.connection_manager.GetConnection(endpoint="/util", payload=payload), multiple=True)
            self.paper_test_types.value = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                "default_paper_test_types"]

        # Existing test entries panel
        with ui.card():
            ui.label("Existing Test Entry Roll table columns to show")
            ui.separator()
            self.paper_test_view_columns = ui.select(options=app.paper_test_view_defaults, multiple=True)
            self.paper_test_view_columns.value = \
                app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                    "test_view_columns"] if app.storage.user.get("preferences")["page_settings"][
                    "paper_test_entry"] else None

        # Existing Test Entries Litho Paper Panel
        with ui.card():
            ui.label("Existing Test Entry Litho table columns to show")
            ui.separator()
            self.litho_paper_test_view_columns = ui.select(options=app.litho_paper_test_view_defaults, multiple=True)
            self.litho_paper_test_view_columns.value = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                "litho_paper_test_view_columns"] if app.storage.user.get("preferences")["page_settings"][
                "paper_test_entry"] else None

    def build_combined_test_entry_pref(self):
        # Searched order panel
        with ui.card():
            ui.label("Searched order columns to show")
            ui.separator()
            self.combined_test_order_cols = ui.select(options=app.order_view_col_defaults, value=
            app.storage.user.get("preferences")["page_settings"]["combined_test_entry"]["order_view_cols"],
                                                      multiple=True)

        # Selected order panel
        with ui.card():
            ui.label("Selected order columns to show")
            ui.separator()
            self.combined_test_selected_order_attrs = ui.select(options=app.combined_test_selected_order_attr_default,
                                                                value=
                                                                app.storage.user.get("preferences")["page_settings"][
                                                                    "combined_test_entry"]["selected_order_attrs"],
                                                                multiple=True)

        # Test Entry panel
        with ui.card():
            ui.label("Default # of tests")
            ui.separator()
            self.combined_test_count = ui.number()
            self.combined_test_count.value = \
                app.storage.user.get("preferences")["page_settings"]["combined_test_entry"][
                    "test_entry_count"] if app.storage.user.get("preferences")["page_settings"][
                    "combined_test_entry"] else 2

        # Test Entry panel
        with ui.card():
            ui.label("Default # of layers")
            ui.separator()
            self.combined_test_layer_count = ui.number()
            self.combined_test_layer_count.value = \
                app.storage.user.get("preferences")["page_settings"]["combined_test_entry"][
                    "layer_count"] if app.storage.user.get("preferences")["page_settings"]["combined_test_entry"] else 2

        # Test Entry panel
        with ui.card():
            ui.label(f"Default test types")
            ui.separator()
            payload = {
                "action": "combined_board_test_types",
                "plant_code": app.storage.user.get("plant"),
            }
            self.combined_test_types = ui.select(
                options=app.connection_manager.GetConnection(endpoint="/util", payload=payload), multiple=True)
            self.combined_test_types.value = app.storage.user.get("preferences")["page_settings"]["combined_test_entry"][
                "default_combined_test_types"]

        # Existing tests panel
        with ui.card():
            ui.label("Existing test columns to show")
            ui.separator()
            self.combined_test_view_cols = ui.select(options=app.combined_test_view_col_default, value=
            app.storage.user.get("preferences")["page_settings"]["combined_test_entry"]["test_view_cols"],
                                                     multiple=True)

    def page_options(self):
        page_options = {}
        for route, page_info in app.pages_dict.items():
            page_options[route] = page_info["title"]
        if app.storage.user.get("type") in ["dev", "super"]:
            for route, page_info in app.dev_dict.items():
                page_options[route] = page_info["title"]
        return page_options

    def submit_click(self):
        user_name = app.storage.user.get("username")
        user_type = app.storage.user.get("type")
        user_auth = app.storage.user.get("authenticated")
        user_plant = app.storage.user.get("plant")
        user_pref = {"landing_page": self.landing_page_select.value,
                     "page_settings": {
                         "dashboard": {"show_3d_graphs": self.show_3d.value},
                         "paper_tests": {
                             "filter_attributes": self.paper_test_filter_select.value,
                             "olv_columns": self.paper_test_olv_select.value
                         },
                         "paper_test_entry": {"test_entry_count": int(self.paper_test_count.value),
                                              "roll_view_columns": self.roll_view_columns.value,
                                              "litho_paper_view_columns": self.litho_paper_view_columns.value,
                                              "test_view_columns": self.paper_test_view_columns.value,
                                              "litho_paper_test_view_columns": self.litho_paper_test_view_columns.value,
                                              "selected_roll_attrs": self.selected_roll_attrs.value,
                                              "selected_litho_attrs": self.selected_litho_attrs.value,
                                              "default_paper_test_types": self.paper_test_types.value,
                                              },
                         "combined_tests": {
                             "filter_attributes": self.combined_test_filter_select.value,
                             "olv_columns": self.combined_test_olv_select.value
                         },
                         "combined_test_entry": {"test_entry_count": int(self.combined_test_count.value),
                                                 "layer_count": int(self.combined_test_layer_count.value),
                                                 "order_view_cols": self.combined_test_order_cols.value,
                                                 "test_view_cols": self.combined_test_view_cols.value,
                                                 "selected_order_attrs": self.combined_test_selected_order_attrs.value,
                                                 "default_combined_test_types": self.combined_test_types.value,
                                                 }
                     }}

        app.storage.user.update({
            "username": user_name,
            "authenticated": user_auth,
            "type": user_type,
            "location": user_plant,
            "preferences": user_pref,
        })

        ui.notify("Updating preferences")
        app.connection_manager.GetConnection(endpoint="/update_preferences",
                                             payload=json.dumps({"username": user_name,
                                                                 "authenticated": user_auth,
                                                                 "type": user_type,
                                                                 "location": user_plant,
                                                                 "preferences": user_pref,
                                                                 }))

    @staticmethod
    async def CallAfter():
        """
        Called from the app level, this is fired after screen rendering, useful for postloading
        """
        app.logger.info("Called After")
