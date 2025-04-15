from core.App import WebApp
from nicegui import app, ui, Client
# In-house components
from data_objects.Utility import UtilityData
from services.Connection import ConnectionManager
from data_objects.Account import AccountData
# In-house services
from local.Logging import Logger
from local.SanitizeInput import Sanitize
from local.globals import *
import time
import json

from fastapi import Request, Response
from fastapi.responses import RedirectResponse


class QualityDashApp(WebApp):
    """
    Subclass of the base WebApp, this is the core of the application
    example use found at the bottom of the file
    title is the name shown in the nav and header throughout the application
    pages dict is a dictionary containing all unrestricted pages to be dynamically created
    storage_secret should likely be updated as master is at deployment, it serves as a
    light security measure for the user's local storage cache, and a reference key
    for loading from it.
    in this class we define a logger app wide, use varies but core example is app.logger.info('hello world')
    this can be called from ANYWHERE inside the app and it will function the same
    app.account_manager is an application wide connection to account data for login,
    additional security in this objects availability may be in order
    app.util_api is an app wide manager for data fetching
    most of this structure should carry over to future projects
    """

    def __init__(self, title='Quality', pages_dict=None, dev_pages=None, storage_secret="ChangeMe"):
        self.error_page()
        # defined app level for use in preferences
        app.pages_dict = self.pages_dict = pages_dict
        app.dev_dict = self.dev_dict = dev_pages
        self.title = title
        # Call the initialize functions and add context data to globals
        app.logger = Logger(__file__)
        app.connection_manager = ConnectionManager()
        app.account_manager = AccountData()
        app.util_api = UtilityData()

        # todo: move all this to mongo
        app.combined_test_filter_defaults = {
            "start_date": {'title': 'Start Date:', 'type': 'date'},
            "end_date": {'title': 'End Date:', 'type': 'date'},
            "order_no": {'title': 'Order #:', 'type': 'string'},
            "author": {'title': 'Author:', 'type': 'account'},
            "plant": {'title': 'Plant:', 'type': 'plant'},
            "flute": {'title': 'Flute:', 'type': 'flute'},
            "type": {'title': 'Test:', 'type': 'combined_test_type'}
        }
        app.paper_test_default_filters = {
            "start_date": {'title': 'Start Date:', 'type': 'date'},
            "end_date": {'title': 'End Date:', 'type': 'date'},
            # Lumping Litho into Roll No for ease of development
            # Really all it is the "primary" filter a user would use
            "roll_no": {'title': 'Roll/Litho #:', 'type': 'string'},
            "author": {'title': 'Author:', 'type': 'account'},
            "plant": {'title': 'Plant:', 'type': 'plant'},
            "grade": {'title': 'Grade:', 'type': 'grade'},
            "type": {'title': 'Type:', 'type': 'paper_type'},
        }
        # Landing page preferences
        app.landing_page = "dashboard"
        # Dashboard preferences
        app.default_show_graphs = False

        # Paper Test preferences
        app.default_paper_test_types = []
        app.paper_test_default_olv_columns = ["ID", "Created", "Roll/Litho #", "Roll Grade/Litho Point", "Roll Type", "Roll Width", "Test Type",
                                              "Test Value"]
        app.roll_view_defaults = ["Roll #", "Grade", "Type", "Width", "Received"]
        app.litho_paper_view_defaults = ["Litho UUID", "Litho Point", "Created At", "Plant Code"]
        app.paper_test_view_defaults = ["Roll #", "Test Reason", "Test Position", "Test Type", "Test Value"]
        app.litho_paper_test_view_defaults = ["Litho UUID", "Litho Point", "Test Type", "Test Reason", "Test Value", "Plant Code"]
        app.selected_roll_attrs = [
            "Roll Number", "Vendor Number", "Vendor Name", "Grade", "Type", "Width",
            "Received Date", "Talley ID", "Vendor Code", "Original Weight",
            "Original Lineal FT", "Original MSF", "Mill", "Moisture", "Plant"]
        app.selected_litho_attrs = ["Litho UUID", "Litho Point", "Created At", "Plant Code"]

        # Combined Board Test preferences
        app.default_test_to_show = 2
        app.default_layers_to_show = 2
        app.default_combined_test_types = []
        app.combined_test_default_olv_columns = ["Order #", "Created", "Plant", "Test", "Flute", "Author", "Test Type",
                                                 "Test Reason", "Test Value"]
        app.order_view_col_defaults = ["Order No", "Customer Name", "Quantity", "Width", "Length", "Plant Code"]
        app.combined_test_view_col_default = ["Order #", "Test Type", "Test Reason", "Test Value"]
        app.combined_test_selected_order_attr_default = ["Order Number", "Plant Code", "Customer Name",
                                                         "Customer Number", "Ship To", "Order Date", "Test",
                                                         "Corrugator ID", "Corrugator Name", "Ship Date", "Customer PO",
                                                         "Spec Code", "Flute Code", "Flute Description", "Length",
                                                         "Width", "Quantity", "Walls",
                                                         ]
        super().__init__(storage_secret)

    async def footer(self):
        """ Over written from parent to include full application name and company name """
        with ui.footer().style('background-color: #349716'):
            with ui.row().classes('w-full no-wrap'):
                ui.label(f'CorrChoice Quality Dashboard')
                ui.space().classes('w-1/2')
                ui.label(f'A Kennedy Technologies Web Application')

    async def construct_login_page(self):
        """
        Over written from parent to add header/footer and alter behavior
        this was an optional step
        """
        ui.page_title(f"{self.title} - Login")
        with ui.header(elevated=True).style('background-color: #349716'):
            ui.label(f'{self.title} - Login').style('font-size: 200%; font-weight: 300')
        with ui.card().classes('absolute-center w-full h-full'):
            with ui.column().classes('absolute-center h-full'):
                with ui.grid(rows=3).classes('w-full'):
                    username = ui.input('Username').classes('center w-full h-full')
                    password = ui.input('Password', password=True, password_toggle_button=True).classes('center w-full h-full')
                    location = ui.select(label='Location:', options=ALL_PLANTS_DICTIONARY, value="")
                ui.button('Log in', on_click=lambda: self.try_login(username=username.value, password=password.value, location=location.value)).classes('center w-full')
        await self.footer()

    def root_page(self):
        """
        dynamically return the root route
        """

        @ui.page(f'/')
        async def dynamic_page():
            """
            this is over written to enable users to set custom home page
            """
            self.user_is_logged_in()
            try:
                ui.open(app.storage.user.get("preferences")['landing_page'])
            except:
                ui.open('/dashboard')
                ui.notify('New User Detected, please apply user preferences in the profile page')

    def ban_hammer(self, request, exception):
        import csv
        from datetime import datetime
        dt = datetime.now()
        ip_address = str(request.client.host)
        url = str(request.url)
        headers = str(request.headers)

        with open("blacklist.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow([ip_address, url, exception, dt, headers])

    def error_page(self):
        @app.exception_handler(404)
        async def exception_handler_404(request: Request, exception: Exception) -> Response:
            if not app.storage.user.get("authenticated"):
                # User not logged in and trying to access non-relevant URL. Add to ban list
                with Client(ui.page('')) as client:
                    ui.label("Oops, we are sorry, the page you were looking for could not be found.").style(
                        "font-size:55px")
                    # Leaving in just in case we want to look at this later
                    # ui.label(str(request.client))
                    # # ui.label(request.user)
                    # ui.label(str(request.cookies))
                    # ui.label(str(request.session))
                    # # ui.label(request.auth)
                    # ui.label(str(request.headers))
                    # for x in request.__dir__():
                    #     ui.label(x)
                    self.ban_hammer(request, exception)
                return client.build_response(request, 404)
            else:
                # User is detected to be logged in, confirmed they have grief credentials. Do not add to ban list
                if app.storage.user.get("landing_page"):
                    return RedirectResponse(app.storage.user.get("landing_page"))
                else:
                    return RedirectResponse("/dashboard")

    def preload(self):
        """
        preload data before rendering screen, sleep simulates loading giving us a load screen
        called in the parent, this is for APP LEVEL CONFIGURATION
        """
        # todo: this needs to be set up to make sure all back end services are available
        time.sleep(1)

    # jaylookhere
    def try_login(self, username=None, password=None, location=None):
        """
        Check the input password against the user entry from the array.
        over write to add user preferences
        """
        s = Sanitize()

        sanitized_username = s.validate_string(username)
        if not sanitized_username:
            app.logger.critical(message=f"Warning username was provided dangerous characters")

        sanitized_password = s.validate_string(password)
        if not sanitized_password:
            app.logger.critical(message=f"Warning password was provided dangerous characters")

        sanitized_location = s.validate_string(location)
        if not sanitized_location:
            app.logger.critical(message=f"Warning location was provided dangerous characters")

        if not sanitized_username or not sanitized_password or not sanitized_location:
            username = ""
            password = ""
            location = ""
            ui.notify("Something went wrong. Please try re-entering the user/pass/location")
            return

        # Collect information from the screen
        payload = {
            "username": sanitized_username,
            "password": sanitized_password,
            "plant": sanitized_location.lower(),
        }

        # Validation
        for key in payload.keys():
            value = payload[key]
            if key == "plant" and len(value) > 2:
                app.logger.warning(message=f"User keyed in a location that is too long ({sanitized_location})")
                time.sleep(1)
                ui.notify("Location doesn't exist. Please try re-entering it.")
                return

        # Authenticate the user
        results = app.connection_manager.GetConnection(endpoint="/authentication", payload=payload)

        # Code to prevent the code breakage when the connection times out
        try:
            status = results["query"][0][0]
        except:
            # This doesn't run because the app times out :/
            ui.notify("Unable to make connection with authentication server. Please contact KTC support.")
            return

        # Results of authentication
        status = results['query'][0][0]
        msg = results['query'][0][1]

        if status == "success":
            app.logger.info("Success authentication detected")
            # Note: if you add another layer to this, use the following code to find the coupled code. (nested_nested_nested_key)
            template_user_preferences = {
                "landing_page": app.landing_page,
                "page_settings": {
                    "dashboard": {"show_3d_graphs": app.default_show_graphs},
                    "paper_tests": {
                        "filter_attributes": [value["title"][:-1] for key, value in
                                              app.paper_test_default_filters.items()],
                        "olv_columns": app.paper_test_default_olv_columns,
                    },
                    "paper_test_entry": {
                        "test_entry_count": app.default_test_to_show,
                        "roll_view_columns": app.roll_view_defaults,
                        "litho_paper_view_columns": app.litho_paper_view_defaults,
                        "test_view_columns": app.paper_test_view_defaults,
                        "litho_paper_test_view_columns": app.litho_paper_test_view_defaults,
                        "selected_roll_attrs": app.selected_roll_attrs,
                        "selected_litho_attrs": app.selected_litho_attrs,
                        "default_paper_test_types": app.default_paper_test_types,
                    },
                    "combined_tests": {
                        "filter_attributes": [value["title"][:-1] for key, value in
                                              app.combined_test_filter_defaults.items()],
                        "olv_columns": app.combined_test_default_olv_columns,
                    },
                    "combined_test_entry": {
                        "test_entry_count": app.default_test_to_show,
                        "layer_count": app.default_layers_to_show,
                        "order_view_cols": app.order_view_col_defaults,
                        "test_view_cols": app.combined_test_view_col_default,
                        "selected_order_attrs": app.combined_test_selected_order_attr_default,
                        "default_combined_test_types": app.default_combined_test_types,
                    },
                }
            }

            # Create the template preferences
            payload["preferences"] = json.dumps(template_user_preferences)

            # Initialize the user for the app
            user_results = app.connection_manager.GetConnection(endpoint="/init_account", payload=payload)

            # Assign storage variables used throughout the application
            app.storage.user.update({
                "authenticated": user_results["authenticated"],
                "username": user_results["username"],
                "plant": user_results["plant"].lower(),
                "type": user_results["type"],
                "preferences": user_results["preferences"]
            })
        elif status == "error":
            app.logger.info("Error authentication detected " + str(msg))
            ui.notify(msg)
        else:
            app.logger.info("Unexpected authentication detected")
            ui.notify("Unexpected error occurred. Try refreshing the page.")

        # Redirect to users preferred home page
        ui.navigate.to(f"/{app.storage.user.get('preferences')['landing_page']}")
# Example implementation, this is also found in main.py of the nicegui front end of the quality dash app
# initialize app
if __name__ in {"__main__", "__mp_main__"}:
    # import pages used in the app
    from pages.CombinedTestEntryPage import CombinedTestEntryPage
    from pages.ModificationScreenManagerPage import ModificationScreenManagerPage
    from pages.TablePage import TablePage
    from pages.PaperTestPage import PaperTestPage
    from pages.DashboardPage import DashboardPage
    from pages.PaperTestEntryPage import PaperTestEntryPage
    from pages.CombinedTestPage import CombinedTestPage

    # Define dictionary of pages to use
    pages_dict = {
        "dashboard": {"title": "Dashboard", "page": DashboardPage},
        "paper_tests": {"title": "Paper Tests", "page": PaperTestPage},
        "paper_test_entry": {"title": "Paper Test Entry", "page": PaperTestEntryPage},
        "combined_tests": {"title": "Combined Tests", "page": CombinedTestPage},
        "combined_test_entry": {"title": "Combined Test Entry", "page": CombinedTestEntryPage},
    }
    dev_pages = {
        'tables': {'title': 'Test Tables', 'page': TablePage},
        'modifications': {'title': 'Modify Tables', 'page': ModificationScreenManagerPage},
    }
    QualityDashApp('Quality Dash', pages_dict, dev_pages, "QDASH")
