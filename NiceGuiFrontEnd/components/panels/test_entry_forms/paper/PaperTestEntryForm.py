from nicegui import ui, app, run
import asyncio
from ..base.TestEntryFormBase import TestEntryFormBase
import json


class PaperTestEntryForm(TestEntryFormBase):
    def __init__(self, parent):
        super().__init__(parent)

        # Setting up the form structure
        self.selected_tab = "Test entry"
        self.panel_tabs = ["Test entry"]

        self.default_test_entries_to_show = app.storage.user.get("preferences")["page_settings"]["paper_test_entry"]['test_entry_count']
        self.test_entries_to_show = self.default_test_entries_to_show

        # Fetching data for the form
        self.test_reasons = app.connection_manager.GetConnection(endpoint="/util",
                                                                 payload={"action": "paper_test_reasons",
                                                                          "plant_code": app.storage.user.get("plant")})
        self.test_types = app.connection_manager.GetConnection(endpoint="/util",
                                                               payload={"action": "paper_test_types",
                                                                        "plant_code": app.storage.user.get("plant")})
        self.test_positions = app.connection_manager.GetConnection(endpoint="/util",
                                                                   payload={"action": "paper_test_positions",
                                                                            "plant_code": app.storage.user.get("plant")})

        self.litho_points = app.connection_manager.GetConnection(endpoint="/util",
                                                                 payload={"action": "lithos",
                                                                          "plant_code": app.storage.user.get("plant")})

        # Storing results of the collected form fields
        self._selected_roll_layer_dict = {}
        self._test_entry_list = []

    # @property
    # def submit_button_enabled(self):
    #     """Controls the enabled state of the submit button."""
    #     # TODO -verify the self.parent
    #     return bool(self.parent.screen_data.roll_no)

    def submit_roll_paper_test_entry(self):
        """Handles the on-click event of the submit button."""
        # Selected Row Panel (Top-right)
        roll_no = self.parent.screen_data.selected_row.get('roll_no')
        vendor = self.parent.screen_data.selected_row.get('vendor_code')
        paper_type = self.parent.screen_data.selected_row.get('inv_tcode')
        grade = self.parent.screen_data.selected_row.get('grade')
        # Plant drop-down (Top-left)
        plant_code = self.parent.screen_data.plant

        list_of_required_desc = ["Roll #", "Plant Code", "Test Reason", "Test Position"]
        list_of_required_code = [roll_no, plant_code, self.test_entries["test_reason"], self.test_entries["test_position"]]
        return_flag = False

        for desc, code in zip(list_of_required_desc, list_of_required_code):
            if not code:
                ui.notify(f"No {desc} is selected!")
                return_flag = True

        if return_flag:
            return

        new_entry = {
            "roll_no": roll_no,
            "plant_code": plant_code,
            "test_reason": self.test_entries["test_reason"],
            "test_position": self.test_entries["test_position"],
            "author": app.storage.user.get("username"),
            "test_entries": {},
            "vendor": vendor,
            "paper_type": paper_type,
            "grade": grade,
        }

        test_entries = {}
        for i in range(0, self.test_entries_to_show):
            test_entries[f"test_{i}"] = self.test_entries["test"][f"test_{i}"]

        new_entry["test_entries"] = json.dumps(test_entries)

        # Fetch the test entries for the panel
        payload = {
            "action": "paper_test",
            "plant_code": f"{self.parent.screen_data.selected_row.get('inv_pcode')}",
            "selected_test_entry": "roll_paper",
        }

        payload.update(new_entry)
        app.logger.info(message=f"payload={payload}", details="Action: Submit Roll Paper test entries")

        asyncio.create_task(self.commit_paper_test_entry(payload=payload))

    def submit_litho_paper_test_entry(self):
        """Handles the on-click event of the submit button."""
        # Selected Row Panel (Top-right)
        litho_uuid = self.parent.screen_data.selected_row.get('litho_uuid')

        # Insurance policy - update the search litho with selected value
        self.parent.screen_data.litho_uuid = litho_uuid

        # Plant drop-down (Top-left)
        plant_code = self.parent.screen_data.plant

        # Test Entry panel (Bottom-left)
        litho_pt = self.test_entries["litho_paper_point"]
        # Input insurance policy
        litho_pt = litho_pt.upper().replace("PT", "")

        list_of_required_desc = ["Litho UUID", "Litho Point", "Plant Code", "Test Reason", "Test Position"]
        list_of_required_code = [litho_uuid, litho_pt, plant_code, self.test_entries["test_reason"], self.test_entries["test_position"]]
        return_flag = False

        for desc, code in zip(list_of_required_desc, list_of_required_code):
            if not code:
                ui.notify(f"No {desc} is selected!")
                return_flag = True

        if return_flag:
            return

        new_entry = {
            "litho_uuid": litho_uuid,
            "plant_code": plant_code,
            "litho_pt": litho_pt,
            "test_reason": self.test_entries["test_reason"],
            "test_position": self.test_entries["test_position"],
            "author": app.storage.user.get("username"),
            "test_entries": {},
        }

        test_entries = {}
        for i in range(0, self.test_entries_to_show):
            test_entries[f"test_{i}"] = self.test_entries["test"][f"test_{i}"]

        new_entry["test_entries"] = json.dumps(test_entries)

        # Fetch the test entries for the panel
        payload = {
            "action": "paper_test",
            "plant_code": f"{plant_code}",
            "selected_test_entry": "litho_paper",
        }

        payload.update(new_entry)
        app.logger.info(message=f"payload={payload}", details="Action: Submit Litho Paper test entries")

        asyncio.create_task(self.commit_paper_test_entry(payload=payload))

    async def commit_paper_test_entry(self, payload=None):
        if payload:
            result_of_committing_test_entry = await run.io_bound(app.connection_manager.GetConnection, endpoint='/commit', payload=payload)
            # if result_of_committing_test_entry:
            #     ui.notify(result_of_committing_test_entry["message"])
            # else:
            #     try:
            #         ui.notify(result_of_committing_test_entry["message"])
            #     except Exception as e:
            #         ui.notify(f"Developer message wasn't provided, something went very wrong with committing the test entries.")

            if result_of_committing_test_entry["success"]:
                # Update the existing tests panel
                self.parent.update_existing_tests()
                self.reset_action()