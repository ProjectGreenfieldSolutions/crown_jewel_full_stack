""" object housing on screen widgets for the paper test page """
# nicegui framework libraries
from nicegui import app, ui, run
import asyncio

# In-house components
from components.panels.filter_panels.FilterPaperTests import FilterPaperTests
from data_objects.PaperTestScreenData import PaperTestScreenData
from components.object_views.PaperTestObjectView import PaperTestObjectView

from pages.NiceKTCPage import NiceKTCPage


class PaperTestPage(NiceKTCPage):
    def __init__(self):
        super().__init__()
        with self:
            # init data object
            self.screen_data = PaperTestScreenData()

            ## Page content here
            # construct a filter panel to allow searching
            self.filter = FilterPaperTests(self)
            # a container is required for proper rendering of the niceview
            with ui.row().style('height: 90vh; width: 100%; display: flex; flex-direction: column;'):
                # construct the table to display found objects
                self.table = PaperTestObjectView()
            # add controls for the table
            with ui.grid(columns=2).classes("w-full"):
                ui.button('Export Paper Tests To CSV',
                          on_click=lambda: self.table.export_data_non_blocking(location="reports/paper_test_data.csv",
                                                                               filename="paper_test_data.csv",
                                                                               format='csv')).classes(
                    'w-full').props("color='orange'")
                ui.button('Export Paper Tests To Excel',
                          on_click=lambda: self.table.export_data_non_blocking(location="reports/paper_test_data.xlsx",
                                                                               filename="paper_test_data.xlsx",
                                                                               format="xlsx")).classes(
                    'w-full').props("color='orange'")

    def populate(self):
        """ though it's not entirely clear, this is actually called from the filter panel's button click event """
        # notify to show functional
        payload = {}
        # Lumping Litho into Roll No for ease of development
        # Really all it is the "primary" filter a user would use
        if self.screen_data.roll_no != "":
            payload['roll_no'] = self.screen_data.roll_no
        if self.screen_data.start_date != "":
            payload['start_date'] = self.screen_data.start_date
        if self.screen_data.end_date != "":
            payload['end_date'] = self.screen_data.end_date
        if self.screen_data.author != "":
            payload['author'] = self.screen_data.author
        if self.screen_data.plant != "":
            payload['plant'] = self.screen_data.plant
        if self.screen_data.grade != "":
            payload['grade'] = self.screen_data.grade
        if self.screen_data.type != "":
            payload['type'] = self.screen_data.type

        ui.notify("Fetching table records...")
        payload["username"] = app.storage.user.get('username')
        asyncio.create_task(self.fetch_filtered_paper_test_data(payload=payload))

    async def fetch_filtered_paper_test_data(self, payload):
        self.screen_data.paper_tests = await run.io_bound(app.connection_manager.GetConnection,
                                                          endpoint="/paper/fetch_tests", payload=payload)

        # with self:
        #     ui.notify(f"{len(self.screen_data.paper_tests['formatted_results'])}" + " unique roll(s) / litho(s) records returned!")
        #     ui.notify(self.screen_data.paper_tests)

        if self.screen_data.paper_tests:
            if self.screen_data.paper_tests["status"] == "success":
                # Remove helper keys for data updating.
                del self.screen_data.paper_tests["status"]
                del self.screen_data.paper_tests["message"]

                # Populate the table with new data
                await self.table.update_data(self.screen_data.paper_tests["formatted_results"])
            elif self.screen_data.paper_tests["status"] == "failed":
                # Display error message
                with self:
                    ui.notify(self.screen_data.paper_tests["message"])

                # Remove helper keys for data updating.
                del self.screen_data.paper_tests["status"]
                del self.screen_data.paper_tests["message"]

