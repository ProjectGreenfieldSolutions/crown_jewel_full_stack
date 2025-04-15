""" Dashboard screen ui, and population called from main->QualityDashApp """
# nicegui library imports
from nicegui import ui, app, run
# in house component imports
from components.panels.ReportPanel import ReportPanel

from pages.NiceKTCPage import NiceKTCPage


class DashboardPage(NiceKTCPage):
    """ This class is a ui card that houses the main page content for the dashboard """

    def __init__(self):
        # super init renders the card widget
        super().__init__()
        # make sure the card uses full screen space available
        with self.classes('w-full h-full'):
            # a grid houses the report panels
            with ui.grid(columns=2):
                #############################################
                # Paper Test Charts
                #############################################
                chart_defs = [
                    {
                        'label': "Paper Tests Per Plant",
                        'graph_types': ['bar', 'pie', 'scatter', 'line'],
                        'graph_attrs': ['plant', 'quantity']
                    }
                ]
                # define the browses of the first report widget
                browse_defs = [{'label': "Paper Tests Per Plant"}]
                # initialize the report widget
                self.rp = ReportPanel(chart_deffs=chart_defs, browse_defs=browse_defs, endpoint="/dashboard", payload={
                    "username": app.storage.user.get("username"),
                    "graph": "paper_tests_per_plant"
                })

                #############################################
                # Combined Board Test Charts
                #############################################
                c_chart_defs = [
                    {
                        'label': "Combined Tests Per Plant",
                        'graph_types': ['bar', 'pie', 'scatter', 'line'],
                        'graph_attrs': ['plant', 'quantity']
                    },
                    # Second chart, if needed
                    {
                        'label': "Combined Test Average Values Per Plant",
                        'graph_types': ['bar', 'pie', 'scatter', 'line'],
                        'graph_attrs': ['plant', 'quantity']
                    }
                ]
                c_browse_defs = [{'label': "Combined Tests Per Plant"}]
                self.crp = ReportPanel(chart_deffs=c_chart_defs, browse_defs=c_browse_defs, endpoint="/dashboard",
                                       payload={
                                           "username": app.storage.user.get("username"),
                                           "graph": "combined_tests_per_plant"
                                       })


    async def CallAfter(self):
        """
        Called from the app level, this is fired after screen rendering, useful for postloading
        """
        app.logger.info("Called After")
        # await the update of both report widgets, force set to false to not overwork redis
        await self.rp.update_report(force_update=False)
        await self.crp.update_report(force_update=False)
