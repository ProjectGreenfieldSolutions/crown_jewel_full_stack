from nicegui import ui, app, run
from ..base.TestEntryFormBase import TestEntryFormBase
import asyncio
import json


class CombinedTestEntryForm(TestEntryFormBase):
    def __init__(self, parent):
        # Variables to structure the form
        super().__init__(parent)

        self.default_test_entries_to_show = app.storage.user.get("preferences")["page_settings"]["combined_test_entry"][
            'test_entry_count']
        self.test_entries_to_show = self.default_test_entries_to_show

        self.selected_tab = "Roll test"
        self.panel_tabs = [self.panel_tabs[0], "Roll test", "Litho test"]
        self.roll_layers = app.connection_manager.GetConnection(endpoint="/util",
                                                                payload={"action": "combined_board_test_layers",
                                                                         "plant_code": app.storage.user.get("plant")})
        self.test_reasons = app.connection_manager.GetConnection(endpoint="/util",
                                                                 payload={"action": "combined_board_test_reasons",
                                                                          "plant_code": app.storage.user.get("plant")})
        self.test_types = app.connection_manager.GetConnection(endpoint="/util",
                                                               payload={"action": "combined_board_test_types",
                                                                        "plant_code": app.storage.user.get("plant")})
        self.litho_points = app.connection_manager.GetConnection(endpoint="/util",
                                                                 payload={"action": "lithos",
                                                                          "plant_code": app.storage.user.get("plant")})

        # Results of the collected form fields
        self._roll_layer_dict = {}
        self._test_entry_list = []

    def create_shown_layers_buttons(self, panel_name: str):
        self.create_button(action="set_roll_layers", text="Set layers to 3", panel=panel_name, selected_tab=panel_name,
                           set_roll_layers=3)
        self.create_button(action="set_roll_layers", text="Set layers to 5", panel=panel_name, selected_tab=panel_name,
                           set_roll_layers=5)
        self.create_button(action="set_roll_layers", text="Set layers to 7", panel=panel_name, selected_tab=panel_name,
                           set_roll_layers=7)

    def create_layer_buttons(self, panel_name: str):
        if self.layers_to_show < len(self.roll_layers):
            self.create_button(action="add", text="Add Layer", panel=panel_name, selected_tab=panel_name)
        if self.layers_to_show > 1:
            self.create_button(action="remove", text="Remove Layer", panel=panel_name, selected_tab=panel_name)

    @ui.refreshable
    def refreshable_test_entry_form(self):
        """ over write of the main ui of this panel, much of the functionality remains the same, but 2 tabs """
        self.populate_selected_test_entry_types()
        with ui.grid(columns=3).classes('w-full'):
            ui.label("Test Entry")
            if self.is_super_user:
                self.create_data_binding_button()
            else:
                ui.space().classes('w-full')
            self.create_reset_button()
        app.logger.info(message=f"Creating combined board test entry form")

        self.tabs = ui.tabs().on("update:model-value", lambda: self.reset_action())
        with self.tabs:
            roll_test_tab = ui.tab("Roll test")
            litho_test_tab = ui.tab("Litho test")

        # Set selected tab
        app.logger.debug(message=f"Setting selected tab")
        test_entry_tab_panels = ui.tab_panels(self.tabs,
                                              value=litho_test_tab if self.selected_tab == "Litho test" else roll_test_tab).classes(
            self.panel_width)

        app.logger.debug(message=f"Applying contents of test entry panels", details=f"TestEntryForm")
        with test_entry_tab_panels:
            # Roll test panel
            with ui.tab_panel(roll_test_tab):
                panel_name = "Roll test"
                with ui.grid(columns=self.panel_columns).classes(self.panel_width):
                    for index, layer in enumerate(self.roll_layers):
                        index += 1
                        if not index > self.layers_to_show and not index > len(self.roll_layers):
                            ui.input(label="Roll Number", placeholder="456456MS",
                                     on_change=lambda e, roll_layer=layer: self.parent.update_roll_verification(e.value,
                                                                                                                roll_layer)).bind_value(
                                self.test_entries['roll'][f'layer_{index}'], "value")
                            ui.select(label="Layer:", options=self.roll_layers, value=layer).bind_value(
                                self.test_entries['roll'][f'layer_{index}'], "layer")

                with ui.grid(columns=3).classes("w-full"):
                    self.create_shown_layers_buttons(panel_name=panel_name)
                with ui.grid(columns=2).classes("w-full"):
                    self.create_layer_buttons(panel_name=panel_name)

                # Test Reason Drop Down
                self.create_test_reason_select()

                # Test Entries
                with ui.grid(columns="auto auto 65px").classes(self.panel_width):
                    self.create_test_entries(self.panel_tabs[0], selected_tab=panel_name)

                ui.button("Submit Roll", on_click=self.submit_test_entry).classes(self.panel_width)
                # ui.button("Submit Roll", on_click=self.submit_test_entry).classes(self.panel_width).bind_enabled_from(self,
                #                                                                                                   'get_submit_roll_button_state')

            # Litho test panel
            with ui.tab_panel(litho_test_tab):
                panel_name = "Litho test"
                with ui.grid(columns=self.panel_columns).classes(self.panel_width):
                    for index, layer in enumerate(self.roll_layers):
                        index += 1
                        if not index > self.layers_to_show:
                            if index == 1:
                                try:
                                    ui.select(label="Litho Point", options=self.litho_points,
                                              value=next(iter(self.litho_points))).bind_value(
                                        self.test_entries['litho'][f'layer_{index}'], "value")
                                except StopIteration as e:
                                    app.logger.warning(message=f"Exception StopIteration detected... {e}")
                            else:
                                ui.input(label="Roll Number", placeholder="456456MS",
                                         on_change=lambda e, roll_layer=layer: self.parent.update_roll_verification(
                                             e.value, roll_layer)).bind_value(
                                    self.test_entries['litho'][f'layer_{index}'], "value")

                            ui.select(label="Layer:", options=self.roll_layers, value=layer).bind_value(
                                self.test_entries['litho'][f'layer_{index}'], "layer")

                    # self.create_layer_buttons(panel_name=panel_name)
                with ui.grid(columns=3).classes("w-full"):
                    self.create_shown_layers_buttons(panel_name=panel_name)
                with ui.grid(columns=2).classes("w-full"):
                    self.create_layer_buttons(panel_name=panel_name)

                # Test Reason Drop Down
                self.create_test_reason_select()

                # Test Entries
                with ui.grid(columns="auto auto 65px").classes(self.panel_width):
                    self.create_test_entries(self.panel_tabs[0], selected_tab=panel_name)
                ui.button("Submit Litho", on_click=self.submit_litho_entry).classes(self.panel_width)
                # ui.button("Submit Litho", on_click=self.submit_litho_entry).classes(self.panel_width).bind_enabled_from(self, 'get_submit_roll_button_state')

    @property
    def submit_button_enabled(self):
        """Controls the enabled state of the submit button."""
        return bool(self.parent.screen_data.selected_row.get("order_no")) or self.can_reset_test_entry_form

    @property
    def get_submit_roll_button_state(self):
        """ This controls the enabled state of the submit button"""
        return self.parent.screen_data.selected_row.get(f"order_no", False)

    def submit_test_entry(self):
        """Handles the on-click event of the submit button."""
        self.submit_entry(entry_type="roll")

    def submit_litho_entry(self):
        """Handles the on-click event of the submit button."""
        self.submit_entry(entry_type="litho")

    def submit_entry(self, entry_type):
        """Handles the on-click event of the submit button."""
        order_no = self.parent.screen_data.selected_row.get('order_no')
        plant_code = self.parent.screen_data.plant
        test_reason = self.test_entries["test_reason"]

        list_of_required_desc = ["Order #", "Plant Code", "Test Reason"]
        list_of_required_code = [order_no, plant_code, test_reason]
        return_flag = False

        for desc, code in zip(list_of_required_desc, list_of_required_code):
            if not code:
                ui.notify(f"No {desc} is selected!")
                return_flag = True

        if return_flag:
            return

        # Prevent double posting of test entry data
        if self.processing_test_entry:
            ui.notify("Data test entry already in process!")
            return
        self.processing_test_entry = True

        new_entry = {
            "order_no": order_no,
            "plant_code": plant_code,
            "test_reason": test_reason,
            "special_instruction_code": self.parent.screen_data.selected_row.get('spec_code'),
            "author": app.storage.user.get("username"),
            "test_entries": {},
        }

        # Load the same-named fields
        for field in ["customer_name", "cust_no", "flute_code",
                      "flute_flute_desc", "corrugator_corru_name", "corru_id", "test_code"]:
            new_entry.update({f"{field}": self.parent.screen_data.selected_row.get(f"{field}")})

        # Load the layer positions and values
        for number in range(1, 8):
            new_entry.update({
                f"layer_position_{number}": self.test_entries[entry_type][f"layer_{number}"]["layer"],
                f"layer_value_{number}": self.test_entries[entry_type][f"layer_{number}"]["value"],
            })

        test_entries = {}
        for i in range(0, self.test_entries_to_show):
            test_entries[f"test_{i}"] = self.test_entries["test"][f"test_{i}"]

        new_entry["test_entries"] = json.dumps(test_entries)

        # Fetch the test entries for the panel
        payload = {
            "action": "combined_board_test",
            "plant_code": f"{self.parent.screen_data.selected_row.get('inv_pcode')}",
        }

        payload.update(new_entry)
        app.logger.info(message=f"payload={payload}", details="Action: Submit combined test entries")

        asyncio.create_task(self.commit_combined_test_entry(payload=payload))

    async def commit_combined_test_entry(self, payload=None):
        if payload:
            result_of_committing_test_entry = await run.io_bound(app.connection_manager.GetConnection,
                                                                 endpoint='/commit', payload=payload)
            # if result_of_committing_test_entry:
            #     ui.notify(result_of_committing_test_entry["message"])
            # else:
                # try:
                #     ui.notify(result_of_committing_test_entry["message"])
                # except Exception as e:
                #     ui.notify(
                #         f"Developer message wasn't provided, something went very wrong with committing the test entries.")

            if result_of_committing_test_entry["success"]:
                # Update the existing tests panel
                self.parent.update_existing_tests()
                self.reset_action()
                self.parent.reset_roll_verification()

        self.processing_test_entry = False
