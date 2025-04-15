# In-house components
from copy import deepcopy

from nicegui import app, ui
from components.widgets.DropDownWidgets import PlantDropDown
from components.object_views.CombinedTestEntryOrderView import CombinedTestEntryOrderView
from components.object_views.CombinedTestEntryTestView import CombinedTestEntryTestView
from components.object_views.PaperTestEntryRollView import PaperTestEntryRollView
from components.object_views.PaperTestEntryLithoView import PaperTestEntryLithoView
from components.object_views.PaperTestEntryTestView import PaperTestEntryTestView
from components.object_views.PaperTestEntryLithoTestView import PaperTestEntryLithoTestView
from components.object_views.RollVerificationView import RollVerificationView
from components.panels.test_entry_forms.paper.PaperTestEntryForm import PaperTestEntryForm
from components.panels.test_entry_forms.combined.CombinedTestEntryForm import CombinedTestEntryForm
from data_objects.TestEntryScreenData import CombinedTestEntryScreenData, PaperTestEntryScreenData
import asyncio

# Drop down widget stuff
from components.widgets.DropDownWidgets import PaperTestPositionDropDown
from components.widgets.DropDownWidgets import PaperTestReasonDropDown
from components.widgets.DropDownWidgets import PaperTestTypeDropDown
from components.widgets.DropDownWidgets import CombinedBoardTestReasonDropDown
from components.widgets.DropDownWidgets import CombinedBoardTestTypeDropDown
from components.widgets.DropDownWidgets import LithosDropDown


class TestEntryContentPanel:

    def __init__(self, title: str = "Paper Test Entry", screen: str = "paper"):
        # Helps determine which screen we're on
        self.title = title
        self.screen = screen
        self.edit_dialog = self.CreateEditDialog()

        # Updates via sub-code
        self.label = None
        self.screen_data = None
        self.search_panel = None
        self.selected_panel = None
        self.selected_paper_entry = "roll_paper"
        self.test_entry_panel = None
        self.roll_verification_panel = None
        self.roll_verification_data = []
        self.existing_tests_panel = None
        self.selected_existing_test = None

    @ui.refreshable
    def CreateSearchPanel(self):
        with ui.card().style("min-height:650px"):
            with ui.grid(columns=3):
                ui.label(f"Search {self.label}")
                ui.space()
                # TODO - Do we want this?
                # ui.button("Clear Search", on_click=self.clear_search).bind_visibility_from(self,
                # "can_clear_search_form")

            ui.separator()

            with ui.grid(columns=2).classes("w-full"):
                if self.screen == "paper":
                    ui.select(options={"roll_paper": "Roll Entry","litho_paper": "Litho Entry"}, value="").bind_value(self, "selected_paper_entry").on_value_change(self.toggle_litho_roll_paper).classes("col-span-full")
                    if self.selected_paper_entry == "roll_paper":
                        ui.input(label="Internal Roll No:", placeholder="123456MS").bind_value(self.screen_data, "roll_no")
                    elif self.selected_paper_entry == "litho_paper":
                        ui.input(label="Litho ID:", placeholder="LL7777777MS or LITHO").bind_value(self.screen_data, "litho_uuid")
                    else:
                        app.logger.error(f"self.selected_paper_entry={self.selected_paper_entry} Search {self.label} input failed")
                elif self.screen == "combined":
                    ui.input(label="Order Number", placeholder="123456").bind_value(self.screen_data, "order_no")
                else:
                    ui.notify("Search panel needs configured")
                PlantDropDown(bind_tuple=(self.screen_data, "plant")).value = app.storage.user.get("plant")
                if self.screen == "paper":
                    if self.selected_paper_entry == "roll_paper":
                        ui.button(f"Search {self.label.capitalize()}", on_click=self.on_click_roll_paper_search).classes("w-full")
                    elif self.selected_paper_entry == "litho_paper":
                        ui.button(f"Search {self.label.capitalize()}", on_click=self.on_click_litho_paper_search).classes("w-full")
                    else:
                        app.logger.error(f"self.selected_paper_entry={self.selected_paper_entry} Search {self.label} submit button failed")
                elif self.screen == "combined":
                    ui.button(f"Search {self.label.capitalize()}", on_click=self.on_click_order_combined_search).classes("w-full")
                else:
                    ui.notify("Search panel button needs configured")

            # Setup the search panel
            if self.screen == "paper":
                if self.selected_paper_entry == "roll_paper":
                    self.search_panel = PaperTestEntryRollView()
                elif self.selected_paper_entry == "litho_paper":
                    self.search_panel = PaperTestEntryLithoView()
                else:
                    app.logger.error(f"self.selected_paper_entry={self.selected_paper_entry} Search {self.label} view failed")
            elif self.screen == "combined":
                self.search_panel = CombinedTestEntryOrderView()
            else:
                ui.notify("Search panel isn't being created")

            self.search_panel.on('rowSelected', self.on_selected_search_row)

            with ui.grid(columns=2).classes("w-full"):
                ui.button(
                    'Export Order(s) To CSV',
                    on_click=lambda: self.search_panel.export_data_non_blocking(
                        location="reports/exported_orders_data.csv",
                        filename="exported_orders.csv",
                        format='csv')).classes(
                    'w-full').props("color='orange'"
                                    ).bind_enabled_from(self, "export_tests_enabled").classes('w-full').props(
                    "color='orange'")
                ui.button(
                    'Export Tests To Excel',
                    on_click=lambda: self.search_panel.export_data_non_blocking(
                        location="reports/exported_orders_data.xlsx",
                        filename="exported_orders.xlsx")
                ).bind_enabled_from(self, "export_tests_enabled").classes('w-full').props("color='orange'")

    @ui.refreshable
    def CreateSelectedPanel(self):
        with ui.card():
            with ui.grid(columns=2):
                ui.label(f"Selected {self.label.capitalize()}")
                ui.button(
                    f"Clear {self.label} selection",
                    on_click=self.clear_selected_panel
                ).props("color='orange'").bind_visibility_from(self, f"search_item_is_selected")

            ui.separator()

            # Display selected roll attributes
            with ui.grid(columns=2 if len(self.screen_data.display_dict.keys()) < 8 else 4):
                # Selected panel
                for attr in self.screen_data.selected_row.keys():
                    if self.screen_data.display_dict[attr] in \
                        app.storage.user.get('preferences')["page_settings"][f"{self.screen}_test_entry"][
                            f'selected_{self.label.lower()}_attrs']:
                        ui.label(f'{self.screen_data.display_dict[attr]}')
                        ui.input().bind_value(self.screen_data.selected_row, f'{attr}').disable()

    @ui.refreshable
    def CreateTestEntryPanel(self):
        with ui.card():
            if self.screen == "paper":
                self.test_entry_panel = PaperTestEntryForm(self)
            elif self.screen == "combined":
                self.test_entry_panel = CombinedTestEntryForm(self)
            else:
                ui.notify("CreateTestEntryPanel")

            self.test_entry_panel.refreshable_test_entry_form()

    @ui.refreshable
    def CreateRollVerificationPanel(self):
        with ui.card().style("min-height:150px"):
            ui.label("Roll Verification")
            ui.separator()
            # Setup the search panel
            if self.screen == "paper":
                self.roll_verification_panel = None
            elif self.screen == "combined":
                self.roll_verification_panel = RollVerificationView()
            else:
                ui.notify("Roll Verification panel isn't being created")

    @ui.refreshable
    def CreateExistingTestsPanel(self):
        with ui.card():
            if self.screen == "paper":
                ui.label(f"Existing Tests {self.label.capitalize()}")
            elif self.screen == "combined":
                # TODO: Come back to add combined test entry variant (dynamic)
                # ui.label(f"Existing Tests {self.label.capitalize()}")
                ui.label(f"Existing Tests Combined Order")
                ui.separator()

            # Setup the selected panel
            if self.screen == "paper":
                if self.selected_paper_entry == "roll_paper":
                    self.existing_tests_panel = PaperTestEntryTestView()
                elif self.selected_paper_entry == "litho_paper":
                    self.existing_tests_panel = PaperTestEntryLithoTestView()
            elif self.screen == "combined":
                self.existing_tests_panel = CombinedTestEntryTestView()
            else:
                ui.notify("Existing Tests Panel  isn't being created")

            self.existing_tests_panel.on('rowSelected', self.on_select_existing_tests)

            # TODO - here
            with ui.grid(columns=2).classes('w-full'):
                self.edit_button = ui.button(
                    "Edit Test",
                    on_click= self.UpdateShowEditDialog

                ).classes('w-full').props("color='green'").bind_enabled_from(self, "is_existing_test_selected")

                self.delete_button = ui.button(
                    "Delete Test",
                    on_click=self.on_click_delete_existing_test
                ).classes('w-full').props("color='red'").bind_enabled_from(self, "is_existing_test_selected")

            with ui.grid(columns=2).classes("w-full"):
                ui.button('Export Paper Tests To CSV',
                          on_click=lambda: self.existing_tests_panel.export_data_non_blocking(
                              location="reports/exported_tests_data.csv",
                              filename="exported_tests_data.csv",
                              format='csv')).classes(
                    'w-full').props("color='orange'"
                                    ).bind_enabled_from(self, "export_tests_enabled").classes('w-full').props(
                    "color='orange'")

                ui.button(
                    'Export Tests To Excel',
                    on_click=lambda: self.existing_tests_panel.export_data_non_blocking(
                        location="reports/exported_tests_data.xlsx",
                        filename="exported_tests_data.xlsx", format='xlsx')
                ).bind_enabled_from(self, "export_tests_enabled").classes('w-full').props("color='orange'")

    def CreateScreen(self):
        self.update_screen_variables()
        with ui.grid(columns=2).classes("w-full"):
            self.CreateSearchPanel()
            self.CreateSelectedPanel()
            self.CreateTestEntryPanel()
            with ui.grid(columns=1).classes("w-full"):
                # Only show this if its Combined Board Test Entry
                if self.screen == "combined":
                    self.CreateRollVerificationPanel()
                self.CreateExistingTestsPanel()

    def update_screen_variables(self):
        if self.screen == "paper":
            self.screen_data = PaperTestEntryScreenData()
            if self.selected_paper_entry == "roll_paper":
                self.label = "Roll"
            elif self.selected_paper_entry == "litho_paper":
                self.label = "Litho"
        elif self.screen == "combined":
            self.screen_data = CombinedTestEntryScreenData()
            self.label = "Order"
        else:
            ui.notify("update_screen_variables needs configured")

    async def update_roll_verification(self, roll_no, roll_layer):
        if len(roll_no) < 8:
            return

        elif len(roll_no) > 8:
            ui.notify(f"To many characters put into roll number field! value=(" + roll_no + ")")
            return

        payload = {
            "roll_no": roll_no,
            "plant": self.screen_data.plant,
        }
        roll_data = app.connection_manager.GetConnection(endpoint="/roll_verification", payload=payload)

        # Acquire the first roll in the returned data
        if roll_data["status"] == "failure":
            ui.notify(f"Roll data ({roll_no}) did not fetch anything from plant ({self.screen_data.plant}) | back end message={roll_data['message']}")
            roll_data = {"roll_no": "NO", "grade": "ROLL", "inv_tcode": "DATA", "vendor_name": "RETURNED!"}
        else:
            roll_data = roll_data["data"]

        was_anything_changed = False
        for roll_layer_value in self.roll_verification_data:
            if roll_layer_value["layer"] == roll_layer.upper():
                roll_layer_value["roll_no"] = roll_data["roll_no"]
                roll_layer_value["grade"] = roll_data["grade"].upper()
                roll_layer_value["type"] = roll_data["inv_tcode"].upper()
                roll_layer_value["vendor"] = roll_data["vendor_name"]
                was_anything_changed = True

        if not was_anything_changed:
            self.roll_verification_data.append(
                {"layer": roll_layer.upper(), "roll_no": roll_data["roll_no"], "grade": roll_data["grade"].upper(),
                 "type": roll_data["inv_tcode"].upper(), "vendor": roll_data["vendor_name"]})

        asyncio.create_task(self.roll_verification_panel.update_data(self.roll_verification_data))

    def reset_roll_verification(self):
        self.roll_verification_data.clear()
        asyncio.create_task(self.roll_verification_panel.update_data(self.roll_verification_data))

    def update_existing_tests(self):
        # Craft the payload used to fetch test_entries
        results = []

        if self.screen == "paper":
            if self.selected_paper_entry == "roll_paper":
                payload = {
                    "roll_no": self.screen_data.roll_no,
                    "plant": self.screen_data.plant,
                }
                endpoint = "/paper/fetch_roll_test_entries"
            elif self.selected_paper_entry == "litho_paper":
                payload = {
                    "litho_uuid": self.screen_data.litho_uuid,
                    "plant": self.screen_data.plant,
                }
                endpoint = "/paper/fetch_litho_test_entries"

        elif self.screen == "combined":
            payload = {
                "order_no": self.screen_data.order_no,
                "plant": self.screen_data.plant,
            }
            endpoint = "/combined/fetch_test_entries"
        else:
            endpoint = ""
            payload = {}

        if endpoint != "" or payload != {}:
            try:
                results = app.connection_manager.GetConnection(endpoint=endpoint, payload=payload)
            except Exception as e:
                msg = f"results failed within update_existing_tests"
                app.logger.error(message=f"{msg} e={e}")
        else:
            ui.notify("update_existing_tests needs configured")

        try:
            # Update the bottom-right panel table with data
            asyncio.create_task(self.existing_tests_panel.update_data(results))
        except Exception as e:
            # Notify user that something is broken in the backend (See FetchPaperTestEntries/FetchCombinedTestEntries)
            msg = f"Updating the exist tests panel failed"
            app.logger.error(message=f"{msg} e={e}")

    def on_click_roll_paper_search(self):
        """
        Handle the search button click event.

        This method triggers a search operation by fetching the paper test results based
        on the provided plant and roll number from the user. The results are then displayed
        in the roll view.
        """
        # Fetch the test results from the backend service
        payload = {
            "roll_no": self.screen_data.roll_no,
            "plant": self.screen_data.plant,
        }

        results = app.connection_manager.GetConnection(endpoint="/paper/search_roll", payload=payload)
        asyncio.create_task(self.search_panel.update_data([value for key, value in results.items()]))

        self.clear_selected_panel()
        self.clear_existing_test_entries()

    def on_click_litho_paper_search(self):
        """
        Handle the search button click event.

        This method triggers a search operation by fetching the paper test results based
        on the provided plant and roll number from the user. The results are then displayed
        in the roll view.
        """
        # Fetch the test results from the backend service
        payload = {
            "plant": self.screen_data.plant,
            "litho_uuid": self.screen_data.litho_uuid,
        }

        if "LL" in self.screen_data.litho_uuid[:2].upper() or "LITHO" in self.screen_data.litho_uuid.upper():
            results = app.connection_manager.GetConnection(endpoint="/paper/search_litho", payload=payload)
            if results:
                if results["status"] == "error":
                    # Output server side message
                    ui.notify(results["message"])
                elif results["status"] == "success":
                    # Output server side message
                    ui.notify(results["message"])

                    # Remove so the following line of code doesn't need to be complicated
                    del results["status"]
                    del results["message"]

                    # Update the web page
                    asyncio.create_task(self.search_panel.update_data([value for key, value in results.items()]))
                else:
                    ui.notify("results 'status' isn't configured properly. Contact KTC Support")
            else:
                ui.notify("No results returned from the server. Contact KTC Support")
        else:
            ui.notify("Invalid entry, please use LL#######MS or LITHO")

        self.clear_selected_panel()
        self.clear_existing_test_entries()

    def on_click_order_combined_search(self):
        """
        Handle the search button click event.

        This method triggers a search operation by fetching the paper test results based
        on the provided plant and roll number from the user. The results are then displayed
        in the roll view.
        """
        # Fetch the test results from the backend service
        payload = {
            "order": self.screen_data.order_no,
            "plant": self.screen_data.plant,
        }
        results = app.connection_manager.GetConnection(endpoint="/combined/search_order", payload=payload)
        asyncio.create_task(self.search_panel.update_data([results]))

        self.clear_selected_panel()
        self.clear_existing_test_entries()

    def on_selected_search_row(self, msg):
        # Clear the bottom-right panel
        self.clear_existing_test_entries()

        # Is the event a row being selected?
        if msg.args["selected"]:
            # Update the selected_row object used to be displayed at the top-right
            self.screen_data.update_selected_panel(msg.args['data'])

            # Map from front-end web page to object used to build the test entry panel
            if self.screen == "paper":
                if self.selected_paper_entry == "roll_paper":
                    self.test_entry_panel.test_entries["roll_no"] = self.screen_data.selected_row["roll_no"]
                elif self.selected_paper_entry == "litho_paper":
                    self.test_entry_panel.test_entries["litho_uuid"] = self.screen_data.selected_row["litho_uuid"]
                    # Insurance policy - update the search litho with selected value
                    self.screen_data.litho_uuid = self.screen_data.selected_row["litho_uuid"]
            elif self.screen == "combined":
                self.test_entry_panel.test_entries["order_no"] = self.screen_data.selected_row["order_no"]
            else:
                ui.notify("on_selected_search_row needs configured")

            # Update the existing test panel (bottom-right)
            self.update_existing_tests()
        else:
            # Clears the selected_row object
            self.clear_selected_panel()

        # Rebuild the panel manually
        self.CreateSelectedPanel.refresh()




    def on_select_existing_tests(self, msg):
        if msg.args["selected"]:
            self.selected_existing_test = msg.args['data']
        else:
            self.selected_existing_test = None

    def on_click_delete_existing_test(self):
        payload = {}
        try:
            app.logger.info(f"Selected existing test ID = {self.selected_existing_test['id']}")
        except Exception as e:
            app.logger.error(f"Whoops - {e}")
            ui.notify("ID for the selected test entry couldn't be found. Try unselecting and re-selecting the target test entry.")
            self.update_existing_tests()
            return


        if self.screen == "paper":
            payload = {
                "id": self.selected_existing_test["id"],
                "test_entry_type": self.selected_paper_entry,
                "plant": self.screen_data.plant,
                "action": "paper_test",
            }
        elif self.screen == "combined":
            payload = {
                "id": self.selected_existing_test["id"],
                "plant": self.screen_data.plant,
                "action": "combined_board_test",
            }

        results = app.connection_manager.GetConnection(endpoint="/delete", payload=payload)
        ui.notify(results["message"])
        self.update_existing_tests()
        self.selected_existing_test = None


    def clear_selected_panel(self):
        # Updates the data for top-right panel
        self.screen_data.update_selected_panel()
        # Rebuilds the top-right panel
        self.CreateSelectedPanel.refresh()
        # Unchecks the search panel (top-left) selected row
        self.search_panel.clear()

    def clear_existing_test_entries(self):
        self.existing_tests_panel.objs.clear()
        self.existing_tests_panel.clear()

    @property
    def search_export_enabled(self):
        # TODO - Confirm
        return bool(self.search_panel.objs)

    @property
    def selected_export_enabled(self):
        # TODO - Confirm
        return bool(self.selected_panel.objs)

    @property
    def existing_tests_export_enabled(self):
        # TODO - Confirm
        return bool(self.existing_tests_view.objs)

    @property
    def is_existing_test_selected(self):
        # TODO - Jay can you figure this out?
        """
            ERROR:
            2024-11-20 04:46:04 /app/components/panels/content_panels/TestEntryBaseContentPanel.py:357:
                                RuntimeWarning: coroutine 'AgGrid.get_selected_row' was never awaited
            2024-11-20 04:46:04   return bool(self.existing_tests_panel.get_selected_row())
        """
        return bool(self.existing_tests_panel.get_selected_row())

    @property
    def search_item_is_selected(self):
        """
        Determine if a roll is currently selected.

        Returns:
        --------
        bool
            True if a roll is selected, False otherwise.
        """
        list_of_valid_items = ["roll_no", "order_no"]
        for item in list_of_valid_items:
            if bool(self.screen_data.selected_row.get(item)):
                return True

        return False

    @property
    def can_clear_search_form(self):
        """
        Determine if the clear search button should be visible.

        Returns:
        --------
        bool
            True if the search form contains any data, False otherwise.
        """
        if self.screen == "paper":
            return bool(self.screen_data.roll_no) or bool(self.screen_data.plant)
        elif self.screen == "combined":
            return bool(self.screen_data.order_no) or bool(self.screen_data.plant)
        else:
            ui.notify("can_clear_search_form needs configured")

    def toggle_litho_roll_paper(self):
        self.label = self.selected_paper_entry.split("_")[0].capitalize()
        self.refresh_page()

    def refresh_page(self):
        app.logger.info("Refreshing page")
        self.CreateSearchPanel.refresh()
        self.CreateSelectedPanel.refresh()
        self.CreateTestEntryPanel.refresh()
        self.CreateRollVerificationPanel.refresh()
        self.CreateExistingTestsPanel.refresh()

    def CreateEditDialog(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('Hello world!')
            ui.button('Close', on_click=dialog.close)
        return dialog

    async def UpdateShowEditDialog(self):
        #TODO: this is not optimal, we should be updating the value of the ui widgets, not clearing and recreating them
        self.edit_dialog.clear()
        test_to_edit = await self.existing_tests_panel.get_selected_row()
        if test_to_edit:
            #{'id': 5215, 'order_no': '456456', 'test_type': 'BCT', 'test_reason': 'Normal Test', 'test_value': 1}
            test_copy = deepcopy(test_to_edit)
            with ui.dialog() as self.edit_dialog, ui.card():
                with ui.grid(columns=2):
                    if self.screen == 'paper':
                        if self.selected_paper_entry == 'litho_paper':
                            ###############################################################
                            # Litho UUID
                            ###############################################################
                            ui.label('Litho UUID:')
                            self.litho_uuid_edit = ui.input(value = test_copy['litho_uuid'])
                            self.litho_uuid_edit.enabled = False

                            ###############################################################
                            # Test Position
                            ###############################################################
                            ui.label('Test Position:')
                            paper_test_position_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "paper_test_position",
                            }

                            paper_test_positions = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                payload=paper_test_position_payload)

                            if paper_test_positions["status"] == "success":
                                del paper_test_positions["status"]
                            elif paper_test_positions["status"] == "failed":
                                # ui.notify(paper_test_positions["message"])
                                del paper_test_positions["status"]
                                del paper_test_positions["message"]

                            paper_test_position = None
                            for key, value in paper_test_positions["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | paper_test_position={test_copy['test_position']}")
                                if value == test_copy['test_position']:
                                    paper_test_position = key
                                    # ui.notify(f"key={key}")
                                    break

                            if test_copy['test_position'] == "null":
                                self.test_position_edit = PaperTestPositionDropDown(bind_tuple=(test_copy, 'test_position'), value="")
                            elif test_copy['test_position'] != "null":
                                self.test_position_edit = PaperTestPositionDropDown(
                                    bind_tuple=(test_copy, 'test_position'), value=paper_test_position)

                            ###############################################################
                            # Test Reason
                            ###############################################################
                            ui.label('Test Reason:')
                            test_reason_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "paper_test_reason",
                            }

                            test_reasons = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                          payload=test_reason_payload)

                            if test_reasons["status"] == "success":
                                del test_reasons["status"]
                            elif test_reasons["status"] == "failed":
                                # ui.notify(test_reasons["message"])
                                del test_reasons["status"]
                                del test_reasons["message"]

                            test_reason = None
                            for key, value in test_reasons["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | test_reason={test_copy['test_reason']}")
                                if value == test_copy['test_reason']:
                                    test_reason = key
                                    # ui.notify(f"key={key}")
                                    break

                            if test_copy['test_reason'] == "null":
                                self.test_reason_edit = PaperTestReasonDropDown(bind_tuple=(test_copy, 'test_reason'), value="")
                            elif test_copy['test_reason'] != "null":
                                self.test_reason_edit = PaperTestReasonDropDown(
                                    bind_tuple=(test_copy, 'test_reason'), value=test_reason)

                            ###############################################################
                            # Test Value
                            ###############################################################
                            ui.label('Test Value:')
                            self.test_value_edit = ui.number(value=test_copy['test_value'],precision=4,step=.0001)

                            ###############################################################
                            # Litho Point
                            ###############################################################
                            ui.label('Litho Point:')

                            litho_point_test_type_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "litho",
                            }
                            lithos = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                    payload=litho_point_test_type_payload)

                            if lithos["status"] == "success":
                                del lithos["status"]
                            elif lithos["status"] == "failed":
                                # ui.notify(lithos["message"])
                                del lithos["status"]
                                del lithos["message"]

                            litho_point = None
                            for key, value in lithos["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | litho_pt={test_copy['litho_pt']}")
                                if f"{value}".upper() == f"{test_copy['litho_pt']}" + "PT":
                                    litho_point = key
                                    # ui.notify(f"key={key}")
                                    break

                            self.litho_point_edit = LithosDropDown(bind_tuple=(test_copy, 'litho_pt'), value=litho_point)

                            ###############################################################
                            # Paper Test Type
                            ###############################################################
                            ui.label('Test Type:')
                            paper_test_type_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "paper_test_type",
                            }
                            paper_test_types = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                    payload=paper_test_type_payload)
                            if paper_test_types["status"] == "success":
                                del paper_test_types["status"]
                            elif paper_test_types["status"] == "failed":
                                # ui.notify(paper_test_types["message"])
                                del paper_test_types["status"]
                                del paper_test_types["message"]

                            paper_test_type = None
                            for key, value in paper_test_types["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | test_type={test_copy['test_type']}")
                                if value == test_copy["test_type"]:
                                    paper_test_type = key
                                    # ui.notify(f"key={key}")
                                    break

                            self.test_type_edit = PaperTestTypeDropDown(bind_tuple=(test_copy, "test_type"), value=paper_test_type)

                            ###############################################################
                            # Buttons
                            ###############################################################
                            ui.button('Cancel', on_click=self.edit_dialog.close)
                            ui.button('Submit', on_click=lambda e: self.UpdateTestEntry(test_to_edit, test_copy))
                        elif self.selected_paper_entry == 'roll_paper':
                            ###############################################################
                            # Roll Number
                            ###############################################################
                            ui.label('Roll Number:')
                            self.roll_no_edit = ui.input(value = test_copy['roll_no'])
                            self.roll_no_edit.enabled = False

                            ###############################################################
                            # Test Position
                            ###############################################################
                            ui.label('Test Position:')
                            paper_test_position_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "paper_test_position",
                            }

                            paper_test_positions = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                        payload=paper_test_position_payload)

                            if paper_test_positions["status"] == "success":
                                del paper_test_positions["status"]
                            elif paper_test_positions["status"] == "failed":
                                # ui.notify(paper_test_positions["message"])
                                del paper_test_positions["status"]
                                del paper_test_positions["message"]

                            paper_test_position = None
                            for key, value in paper_test_positions["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | paper_test_position={test_copy['test_position']}")
                                if value == test_copy['test_position']:
                                    paper_test_position = key
                                    # ui.notify(f"key={key}")
                                    break

                            if test_copy['test_position'] == "null":
                                self.test_position_edit = PaperTestPositionDropDown(bind_tuple=(test_copy, 'test_position'), value="")
                            elif test_copy['test_position'] != "null":
                                self.test_position_edit = PaperTestPositionDropDown(
                                    bind_tuple=(test_copy, 'test_position'), value=paper_test_position)

                            ###############################################################
                            # Test Reason
                            ###############################################################
                            ui.label('Test Reason:')

                            test_reason_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "paper_test_reason",
                            }

                            test_reasons = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                payload=test_reason_payload)

                            if test_reasons["status"] == "success":
                                del test_reasons["status"]
                            elif test_reasons["status"] == "failed":
                                # ui.notify(test_reasons["message"])
                                del test_reasons["status"]
                                del test_reasons["message"]

                            test_reason = None
                            for key, value in test_reasons["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | test_reason={test_copy['test_reason']}")
                                if value == test_copy['test_reason']:
                                    test_reason = key
                                    # ui.notify(f"key={key}")
                                    break

                            if test_copy['test_reason'] == "null":
                                self.test_reason_edit = PaperTestReasonDropDown(bind_tuple=(test_copy, 'test_reason'), value="")
                            elif test_copy['test_reason'] != "null":
                                self.test_reason_edit = PaperTestReasonDropDown(
                                    bind_tuple=(test_copy, 'test_reason'), value=test_reason)

                            ###############################################################
                            # Test Value
                            ###############################################################
                            ui.label('Test Value:')
                            self.test_value_edit = ui.number(value=test_copy['test_value'],precision=4,step=.0001)

                            ###############################################################
                            # Paper Test Type
                            ###############################################################
                            ui.label('Test Type:')
                            paper_test_type_payload = {
                                "plant_code": app.storage.user.get("plant"),
                                "target_model": "paper_test_type",
                            }
                            paper_test_types = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                    payload=paper_test_type_payload)
                            if paper_test_types["status"] == "success":
                                del paper_test_types["status"]
                            elif paper_test_types["status"] == "failed":
                                # ui.notify(paper_test_types["message"])
                                del paper_test_types["status"]
                                del paper_test_types["message"]

                            paper_test_type = None
                            for key, value in paper_test_types["key_value_pairs"].items():
                                # ui.notify(f"all key={key} | all value={value} | test_type={test_copy['test_type']}")
                                if value == test_copy["test_type"]:
                                    paper_test_type = key
                                    # ui.notify(f"key={key}")
                                    break

                            self.test_type_edit = PaperTestTypeDropDown(bind_tuple=(test_copy, "test_type"), value=paper_test_type)

                            ###############################################################
                            # Buttons
                            ###############################################################
                            ui.button('Cancel', on_click=self.edit_dialog.close)
                            ui.button('Submit', on_click=lambda e:self.UpdateTestEntry(test_to_edit, test_copy))

                    elif self.screen == 'combined':
                        ###############################################################
                        # Order Number
                        ###############################################################
                        ui.label('Order Number:')
                        self.order_no_edit = ui.input(value = test_copy['order_no'])
                        self.order_no_edit.enabled = False

                        ###############################################################
                        # Combined Test Type
                        ###############################################################
                        ui.label('Test Type:')
                        combined_test_type_payload = {
                            "plant_code": app.storage.user.get("plant"),
                            "target_model": "combined_test_type",
                        }
                        combined_test_types = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                                payload=combined_test_type_payload)
                        if combined_test_types["status"] == "success":
                            del combined_test_types["status"]
                        elif combined_test_types["status"] == "failed":
                            # ui.notify(combined_test_types["message"])
                            del combined_test_types["status"]
                            del combined_test_types["message"]

                        combined_test_type = None
                        for key, value in combined_test_types["key_value_pairs"].items():
                            # ui.notify(f"all key={key} | all value={value} | test_type={test_copy['test_type']}")
                            if value == test_copy["test_type"]:
                                combined_test_type = key
                                # ui.notify(f"key={key}")
                                break

                        self.test_type_edit = CombinedBoardTestTypeDropDown(bind_tuple=(test_copy, "test_type"),
                                                                    value=combined_test_type)

                        ###############################################################
                        # Test Reason
                        ###############################################################
                        ui.label('Test Reason:')

                        test_reason_payload = {
                            "plant_code": app.storage.user.get("plant"),
                            "target_model": "combined_test_reason",
                        }

                        test_reasons = app.connection_manager.GetConnection(endpoint="/fetch_model",
                                                                            payload=test_reason_payload)

                        if test_reasons["status"] == "success":
                            del test_reasons["status"]
                        elif test_reasons["status"] == "failed":
                            # ui.notify(test_reasons["message"])
                            del test_reasons["status"]
                            del test_reasons["message"]

                        test_reason = None
                        for key, value in test_reasons["key_value_pairs"].items():
                            # ui.notify(f"all key={key} | all value={value} | test_reason={test_copy['test_reason']}")
                            if value == test_copy['test_reason']:
                                test_reason = key
                                # ui.notify(f"key={key}")
                                break

                        if test_copy['test_reason'] == "null":
                            self.test_reason_edit = CombinedBoardReasonDropDown(bind_tuple=(test_copy, 'test_reason'),
                                                                            value="")
                        elif test_copy['test_reason'] != "null":
                            self.test_reason_edit = CombinedBoardTestReasonDropDown(
                                bind_tuple=(test_copy, 'test_reason'),
                                value=test_reason)

                        ui.label('Test Value:')
                        self.test_value_edit = ui.number(value=test_copy['test_value'],precision=3,step=.001)

                        ###############################################################
                        # Buttons
                        ###############################################################
                        ui.button('Cancel', on_click=self.edit_dialog.close)
                        ui.button('Submit', on_click=lambda e:self.UpdateTestEntry(test_to_edit, test_copy))

            self.edit_dialog.open()

    def UpdateTestEntry(self, old, new):
        if old['id'] == new['id']:
                if self.screen == "paper":
                    update_data = {
                        "plant": self.screen_data.plant,
                        'id': new['id'],
                        'test_position': self.test_position_edit.value,
                        'test_reason': self.test_reason_edit.value,
                        'test_type': self.test_type_edit.value,
                        'test_value': self.test_value_edit.value
                    }
                elif self.screen == "combined":
                    update_data = {
                        "plant": self.screen_data.plant,
                        'id': new['id'],
                        'test_reason': self.test_reason_edit.value,
                        'test_type': self.test_type_edit.value,
                        'test_value': self.test_value_edit.value
                    }
                else:
                    app.logger.error("UpdateTestEntry screen not detected...")

                for key in update_data.keys():
                    if not update_data[key]:
                        ui.notify(f"key={key} needs a proper value")
                        return

                if self.screen == 'paper':
                    update_data.update({
                        "action": "paper_test",
                        "selected_test_entry": self.selected_paper_entry
                    })

                    if self.selected_paper_entry == 'litho_paper':
                        update_data.update({
                            'litho_uuid': self.litho_uuid_edit.value,
                            'litho_pt': self.litho_point_edit.value.lower().replace("pt", "")
                        })
                    elif self.selected_paper_entry == 'roll_paper':
                        # TODO - Confirm this is working
                        update_data.update({
                        'roll_no': self.roll_no_edit.value,

                        })
                    else:
                        ui.notify('Update call needs to be configured')

                elif self.screen == 'combined':
                    # TODO - Confirm this is working
                    update_data.update({
                        "action": "combined_board_test",
                        'order_no': self.order_no_edit.value
                    })
                else:
                    ui.notify('Update call needs to be configured')
                #commit them
                app.connection_manager.GetConnection(endpoint='/commit', payload=update_data)

        self.edit_dialog.close()
        self.update_existing_tests()
