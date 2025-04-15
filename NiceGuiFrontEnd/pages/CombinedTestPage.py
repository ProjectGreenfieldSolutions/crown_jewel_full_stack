from nicegui import ui, app, run
from components.panels.filter_panels.FilterCombinedTests import FilterCombinedTests
from data_objects.CombinedTestScreenData import CombinedTestScreenData
from components.object_views.CombinedTestObjectView import CombinedTestObjectView
import asyncio

from pages.NiceKTCPage import NiceKTCPage


class CombinedTestPage(NiceKTCPage):
    def __init__(self):
        super().__init__()
        with self:
            self.screen_data = CombinedTestScreenData()
            self.filter = FilterCombinedTests(self)
            with ui.row().style('height: 90vh; width: 100%; display: flex; flex-direction: column;'):
                self.table = CombinedTestObjectView()
            with ui.grid(columns=2).classes("w-full"):
                ui.button('Export Combined Tests To CSV',
                          on_click=lambda: self.table.export_data_non_blocking(location="reports/combined_tests_data.csv",
                                                                               filename="combined_tests.csv",
                                                                               format='csv')).classes(
                    'w-full').props("color='orange'")
                ui.button('Export Combined Tests To Excel',
                          on_click=lambda: self.table.export_data_non_blocking(location="reports/combined_tests_data.xlsx",
                                                                               filename="combined_tests.xlsx")
                          ).classes(
                    'w-full').props("color='orange'")

    def populate(self):
        payload = {}
        if self.screen_data.order_no != "":
            payload['order_no'] = self.screen_data.order_no
        if self.screen_data.start_date != "":
            payload['start_date'] = self.screen_data.start_date
        if self.screen_data.end_date != "":
            payload['end_date'] = self.screen_data.end_date
        if self.screen_data.author != "":
            payload['author'] = self.screen_data.author
        if self.screen_data.plant != "":
            payload['plant'] = self.screen_data.plant
        if self.screen_data.flute != "":
            payload['flute'] = self.screen_data.flute
        if self.screen_data.type != "":
            payload['type'] = self.screen_data.type

        ui.notify("Fetching table records...")
        payload["username"] = app.storage.user.get('username')
        asyncio.create_task(self.fetch_filtered_combined_test_data(payload=payload))

    async def fetch_filtered_combined_test_data(self, payload):
        self.screen_data.combined_tests = await run.io_bound(app.connection_manager.GetConnection,
                                                             endpoint="/combined/fetch_tests", payload=payload)

        if self.screen_data.combined_tests["status"] == "success":
            # Remove helper keys for data updating.
            del self.screen_data.combined_tests["status"]
            del self.screen_data.combined_tests["message"]

            # Populate the table with new data
            await self.table.update_data(list(self.screen_data.combined_tests["formatted_results"]))
        elif self.screen_data.combined_tests["status"] == "failed":
            # Display error message
            with self:
                ui.notify(self.screen_data.combined_tests["message"])

            # Remove helper keys for data updating.
            del self.screen_data.combined_tests["status"]
            del self.screen_data.combined_tests["message"]


