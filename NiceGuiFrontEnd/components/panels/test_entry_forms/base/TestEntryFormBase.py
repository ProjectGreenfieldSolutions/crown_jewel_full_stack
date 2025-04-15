from nicegui import ui, app
from copy import deepcopy


class TestEntryFormBase:
    def __init__(self, parent):
        # Cache reference to parent for data binding
        self.parent = parent

        self.processing_test_entry = False

        # Defaults
        self.default_test_entries_to_show = 9
        self.default_layers_to_show = 3
        self.default_test_entries = {
            # Paper Test
            "roll_no": "",
            "test_position": "",
            "litho_paper_point": 0,

            # Combined
            "order_no": "",
            "litho": {
                "layer_1": {"value": "", "layer": "l1"},
                "layer_2": {"value": "", "layer": "m1"},
                "layer_3": {"value": "", "layer": "l2"},
                "layer_4": {"value": "", "layer": "m2"},
                "layer_5": {"value": "", "layer": "l3"},
                "layer_6": {"value": "", "layer": "m3"},
                "layer_7": {"value": "", "layer": "l4"},
            },
            "roll": {
                "layer_1": {"value": "", "layer": "l1"},
                "layer_2": {"value": "", "layer": "m1"},
                "layer_3": {"value": "", "layer": "l2"},
                "layer_4": {"value": "", "layer": "m2"},
                "layer_5": {"value": "", "layer": "l3"},
                "layer_6": {"value": "", "layer": "m3"},
                "layer_7": {"value": "", "layer": "l4"},
            },
            # Both
            "test_reason": "",
            "test": {
                "test_0": {"value": "0", "type": ""},
                "test_1": {"value": "0", "type": ""},
                "test_2": {"value": "0", "type": ""},
                "test_3": {"value": "0", "type": ""},
                "test_4": {"value": "0", "type": ""},
                "test_5": {"value": "0", "type": ""},
                "test_6": {"value": "0", "type": ""},
                "test_7": {"value": "0", "type": ""},
                "test_8": {"value": "0", "type": ""},
                "test_9": {"value": "0", "type": ""},
            },
        }
        self.panel_columns = 2
        self.panel_width = "w-full"

        # State variables
        self.selected_tab = None
        self.tabs = None
        self.panel_tabs = ["Test entry"]
        self.layers_to_show = app.storage.user.get("preferences")["page_settings"]["combined_test_entry"]['layer_count']
        self.test_entries_to_show = self.default_test_entries_to_show
        self.roll_layers = {}
        self.litho_points = {}
        self.test_positions = {}
        self.test_reasons = {}
        self.test_types = {}
        self.test_entries = deepcopy(self.default_test_entries)
        self.selected_test_entry_types = {}
        self.refresh_displayed_test_entry_types()

    def refresh_displayed_test_entry_types(self):
        # PROFILE SCREEN
        if self.parent.screen == "paper":
            payload = {
                "plant_code": app.storage.user.get("plant"),
                "action": "paper_test_types",
            }
        elif self.parent.screen == "combined":
            payload = {
                "plant_code": app.storage.user.get("plant"),
                "action": "combined_board_test_types",
            }
        else:
            payload = {}
            ui.notify("create_test_entries needs configured")

        # Fetch the Test Type from Django database
        self.selected_test_entry_types = app.connection_manager.GetConnection(endpoint="/util", payload=payload)

        # Reorder test types based on user profile settings
        self.organize_test_types()

    def organize_test_types(self):
        """ Designed to specifically reorganize the order of the dictionary that displays the test entry types on both paper / combined test entry panels"""
        if self.parent.screen == "paper":
            default_types = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"][
                "default_paper_test_types"]
        elif self.parent.screen == "combined":
            default_types = app.storage.user.get("preferences")["page_settings"]["combined_test_entry"][
                "default_combined_test_types"]
        else:
            default_types = []

        # Use default selected test types
        new_types_list = []
        for type in default_types:
            new_types_list.append(type)

        # Load in remainder test types
        for key, value in self.selected_test_entry_types.items():
            if not key in new_types_list:
                new_types_list.append(key)

        # Temporary dictionary to resort selected test entry dictionary
        temp_dict = {}

        # Recreate the test type dictionary
        for key in new_types_list:
            temp_dict[key] = self.selected_test_entry_types[key]

        # Commit updated test types
        self.selected_test_entry_types = deepcopy(temp_dict)

    def refresh_test_entries_dictionary(self):
        for idx, (key, value) in enumerate(self.test_entries["test"].items()):
            if idx + 1 <= self.test_entries_to_show:
                self.test_entries["test"][f"test_{idx}"]["type"] = ""
                self.test_entries["test"][f"test_{idx}"]["value"] = "0"

    def populate_selected_test_entry_types(self):
        self.refresh_test_entries_dictionary()
        for idx, (code, desc) in enumerate(self.selected_test_entry_types.items()):
            if idx + 1 <= self.test_entries_to_show:
                self.test_entries["test"][f"test_{idx}"]["type"] = code

    def update_selected_tab(self, tab):
        self.selected_tab = tab

    def create_data_binding_button(self):
        return ui.button(
            "Show Data Binding",
            on_click=self.show_data_binding
        ).props(f"color='orange'").bind_visibility_from(self, "is_super_user")

    def create_reset_button(self):
        return ui.button(
            "Reset form",
            on_click=self.reset_action
        ).bind_visibility_from(self, 'can_reset_test_entry_form').props(f"color='orange'")

    def create_button(self, action: str, text: str, panel: str, selected_tab: str = None, set_roll_layers=None):
        valid_actions = ["add", "remove", "set_roll_layers"]
        if action not in valid_actions:
            app.logger.error(f"Invalid button action: {action}")
            return

        if panel not in self.panel_tabs:
            app.logger.error(f"Invalid panel type: {panel}")
            return

        if action == "add":
            background_color = "green"
        elif action == "remove":
            background_color = "red"
        elif action == "set_roll_layers":
            background_color = "blue"
        else:
            ui.notify("WARNING - Default background color set for button")
            background_color = "purple"

        if panel in ["Litho test", "Roll test"]:
            if action == "set_roll_layers":
                return ui.button(
                    text,
                    on_click=lambda: self.change_shown_layers(action, selected_tab, override_value=set_roll_layers)
                ).props(f"color='{background_color}'")
            else:
                return ui.button(
                    text,
                    on_click=lambda: self.change_shown_layers(action, selected_tab)
                ).props(f"color='{background_color}'")
        else:
            return ui.button(
                text,
                on_click=lambda: self.change_shown_test_entries(action, selected_tab)
            ).props(f"color='{background_color}'")

    def reset_action(self):
        self.test_entries = deepcopy(self.default_test_entries)
        self.refresh_test_entries_dictionary()
        self.refresh_displayed_test_entry_types()
        self.populate_selected_test_entry_types()
        self.selected_tab = self.tabs.value
        self.layers_to_show = self.default_layers_to_show
        self.test_entries_to_show = self.default_test_entries_to_show
        self.refreshable_test_entry_form.refresh()
        if self.parent.screen == "combined":
            self.parent.reset_roll_verification()

    def show_data_binding(self):
        ui.notify(self.test_entries)

    def create_test_reason_select(self, span: str = "", size: str = "w-full"):
        try:
            return ui.select(
                label="Test(s) Reason:",
                options=self.test_reasons,
                value=next(iter(self.test_reasons))
            ).bind_value(self.test_entries, "test_reason").classes(f"{span} {size}")
        except StopIteration as e:
            app.logger.warning(f"StopIteration detected: {e}")

    def create_litho_point_select(self, span: str = "", size: str = "w-full"):
        try:
            return ui.select(
                label="Litho Test Point:",
                options=self.litho_points,
                value=next(iter(self.litho_points))
            ).bind_value(self.test_entries, 'litho_paper_point').classes(f"{span} {size}")
        except StopIteration as e:
            app.logger.warning(f"StopIteration detected: {e}")

    def create_test_position_select(self, span: str = "", size: str = "w-full"):
        try:
            return ui.select(
                label="Test(s) Position:",
                options=self.test_positions,
                value=next(iter(self.test_positions))
            ).bind_value(self.test_entries, 'test_position').classes(f"{span} {size}")
        except StopIteration as e:
            app.logger.warning(f"StopIteration detected: {e}")

    def change_shown_test_entries(self, action: str, tab: str):
        app.logger.debug(f"Changing test entries shown: {action}")
        self.selected_tab = tab

        if action == "add":
            self.test_entries_to_show += 1
            message = "Test entry added!"
            # Uncomment for a limit of test entries
            # if self.test_entries_to_show < self.default_test_entries_to_show:
            #     self.test_entries_to_show += 1
            #     message = "Test entry added!"
            # else:
            #     message = f"Maximum test entries added! ({self.default_test_entries_to_show})"
        elif action == "remove" and self.test_entries_to_show > 1:
            self.test_entries_to_show -= 1
            message = "Test entry removed!"
        else:
            message = "Can't remove anymore test entries!"
        self.refreshable_test_entry_form.refresh()
        ui.notify(message)
        app.logger.debug(message)

    def update_test_entry_types(self, iteration):
        key = self.test_entries["test"][f"test_{iteration}"]["type"]
        if key:
            del self.selected_test_entry_types[key]

        if self.test_entries_to_show > 1:
            self.test_entries_to_show -= 1

        self.refreshable_test_entry_form.refresh()

    def create_test_entries(self, panel: str, selected_tab: str = None):
        # Update the data bound dictionary, if possible
        # if types:
        #     for index, key in enumerate(types.keys()):
        #         try:
        #             self.test_entries['test'][f"test_{index}"]["type"] = key
        #         except Exception as e:
        #             pass

        # Create the selection drop-downs on the web page
        for i in range(0, self.test_entries_to_show):
            try:
                # Note: This line trips the exception, causing the initial portion of this ui creation to get bypassed
                tripwire = f"test_" + str(i)
                app.logger.debug(message=f"Does this entry exist? {self.test_entries['test'][tripwire]}")
            except Exception as e:
                # Code to execute if try fails
                self.test_entries["test"][f"test_{i}"] = {"type": "", "value": "0"}
            else:
                # Code to execute if try is successful
                pass
            finally:
                # Performs this code block every time
                ui.number(
                    label=f"Test Value",
                    placeholder=1.234,
                    precision=3,
                    step=.001
                ).bind_value(self.test_entries["test"][f"test_{i}"], "value")

                ui.select(
                    label=f"Test Type",
                    options=self.test_types,
                ).bind_value(self.test_entries["test"][f"test_{i}"], "type")

                ui.button("X", on_click=lambda iter=i: (
                    self.update_test_entry_types(iter), self.refreshable_test_entry_form.refresh())).props(
                    "color='red'")

        self.create_button("add", "Add Test Entry", panel=panel, selected_tab=selected_tab).classes("col-span-full")

        # TODO - determine whether to keep after project goes live (Need user feedback)
        # Keeping for legacy purpose?
        # if self.test_entries_to_show > 1:
        #     self.create_button("remove", "Remove Test Entry", panel=panel, selected_tab=selected_tab)

    @ui.refreshable
    def refreshable_test_entry_form(self):
        """ refreshable decorator to allow update via self.refreshable_test_entry_form.refresh() """
        # Rebuild the list of test entry types to display to screen
        self.populate_selected_test_entry_types()

        with ui.grid(columns=3).classes('w-full'):
            if self.parent.screen == "paper":
                ui.label(f"Test Entry {self.parent.label.capitalize()}")
            elif self.parent.screen == "combined":
                # TODO: Come back to add combined test entry variant (dynamic)
                # ui.label(f"Test Entry {self.parent.label.capitalize()}")
                ui.label(f"Test Entry Combined Order")

            if self.is_super_user:
                self.create_data_binding_button()
            else:
                ui.space().classes('w-full')
            self.create_reset_button()

        ui.separator()
        app.logger.info("Creating test entry form")

        with ui.grid(columns=2).classes("w-full"):
            self.create_test_reason_select()
            self.create_test_position_select()
            if self.parent.selected_paper_entry == "litho_paper":
                self.create_litho_point_select(span="col-span-full")

        self.tabs = ui.tabs().on("update:model-value", lambda: self.reset_action())
        with self.tabs:
            test_entry_tab = ui.tab(self.panel_tabs[0])

        test_entry_tab_panels = ui.tab_panels(self.tabs, value=test_entry_tab).classes(self.panel_width)

        with test_entry_tab_panels:
            with ui.tab_panel(self.panel_tabs[0]):
                with ui.grid(columns="auto auto 65px").classes(self.panel_width):
                    self.create_test_entries(self.panel_tabs[0])

        if self.parent.screen == "paper":
            if self.parent.selected_paper_entry == "roll_paper":
                ui.button(f"Submit Test Entries {self.parent.label.capitalize()}", on_click=self.submit_roll_paper_test_entry).classes(self.panel_width)
            elif self.parent.selected_paper_entry == "litho_paper":
                ui.button(f"Submit Test Entries {self.parent.label.capitalize()}", on_click=self.submit_litho_paper_test_entry).classes(self.panel_width)
        elif self.parent.screen == "combined":
            ui.button("Submit Test Entries", on_click=self.submit_test_entry).classes(self.panel_width)
        # ui.button(
        #     "Submit Test Entries",
        #     on_click=self.submit_test_entry
        # ).classes(self.panel_width).bind_enabled_from(self, 'submit_button_enabled')

    def change_shown_layers(self, action: str, tab: str, override_value=None):
        app.logger.debug(f"Changing layers shown: {action}")
        self.selected_tab = tab

        if not override_value:
            if action == "add" and self.layers_to_show < len(self.roll_layers):
                self.layers_to_show += 1
                message = "Test entry layer added!"
            elif action == "remove" and self.layers_to_show > 1:
                self.layers_to_show -= 1
                message = "Test entry layer removed!"
            else:
                message = "Can't change layers anymore!"

            self.refreshable_test_entry_form.refresh()
            ui.notify(message)
            app.logger.debug(message)
        else:
            # Directly sets the shown layers
            if 1 <= override_value <= 7:
                self.layers_to_show = override_value
                self.refreshable_test_entry_form.refresh()
                ui.notify(f"Set roll layers to {override_value}")
            else:
                ui.notify(
                    f"ERROR - number of shown layers attempting to be set to {override_value} which is outside of the limits")

    @property
    def submit_button_enabled(self):
        """Override to control the enabled state of the submit button."""
        return False

    def submit_test_entry(self):
        """Override this method in a subclass."""
        ui.notify("Please implement this method in a subclass")

    def submit_roll_paper_test_entry(self):
        """Override this method in a subclass."""
        ui.notify("Please implement this method in a subclass")

    def submit_litho_paper_test_entry(self):
        """Override this method in a subclass."""
        ui.notify("Please implement this method in a subclass")

    def submit_litho_entry(self):
        """Override this method in a subclass."""
        ui.notify("Please implement this method in a subclass")

    def user_is_logged_in(self):
        if not app.storage.user.get('authenticated', False):
            app.logger.warning('user not auth')
            return ui.open('/login')

    @property
    def is_super_user(self):
        """Override this to check user permissions."""
        self.user_is_logged_in()
        if app.storage.user['type'] not in ['dev', 'super']:
            return False
        return True

    @property
    def can_reset_test_entry_form(self):
        for i in range(self.test_entries_to_show):
            if self.test_entries.get(f'layer_{i}.test_value') is not None:
                return True
        return False
