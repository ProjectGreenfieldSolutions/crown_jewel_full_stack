""" Report Panel for use in any report needing a method of visualizing data """

from datetime import datetime
from nicegui import ui, run, app

from components.object_views.ReportBrowse import ReportBrowse
from components.MultiChart import MultiChart


class ReportPanel(ui.card):
    """
    a panel housing widgets allowing the visualization of data from an endpoint

      params:
              chart_deffs: [{}]
                  ex.
                  [
                      {
                          'label': "Paper Tests Per Plant",
                          'graph_types': ['bar', 'pie', 'scatter', 'line'],
                          'graph_attrs': ['plant', 'quantity']
                      }
                  ]
                  # define the browses of the first report widget
              browse_defs: [{}]
                  ex.
                  [{'label': "Paper Tests Per Plant"}]
              endpoint: str
                  ex.
                  "/dashboard"
              payload: {}
                  ex.
                  {
                  "username": app.storage.user.get("username"),
                  "graph": "paper_tests_per_plant"
                  }
    """

    def __init__(self, chart_deffs, browse_defs, endpoint, payload):
        super().__init__()
        with self:
            # here we initialize values
            self.chart_configs = chart_deffs
            self.chart_widgets = []
            self.browse_configs = browse_defs
            self.browse_widgets = []
            self.endpoint = endpoint
            self.payload = payload
            self.last_updated = ''

            # then finally, render the screen
            self.render_widgets()

    def render_widgets(self):
        """ render the ui to the screen"""
        # make a card to house the widgets
        with ui.card() as self.main_content:
            # for each config set in init
            for chart_deff in self.chart_configs:
                config = list(chart_deff.values())
                # make a multichart
                self.chart_widgets.append(MultiChart(config[0]))
            # for each browse config
            for config in self.browse_configs:
                # make a browse
                # todo: enable the setting of headers per browse to set up custom views
                self.browse_widgets.append(ReportBrowse(config['label']))
            # get the graph types configured
            options = self.chart_configs[0]['graph_types']
            options.append('browse')
            # a selector for what type of visualizer to display the data with
            self.selector_widget = ui.select(options=options, value='pie').on_value_change(self.selector_widget_changed)
            # a button to force an api endpoint update
            self.update_button = ui.button(
                f"Last Updated - {self.last_updated if self.last_updated != '' else 'Unknown'} Update Now").on('click',
                                                                                                               lambda
                                                                                                                   e: self.update_report())
            # for chartwidget on the screen
            for w in self.chart_widgets:
                # each chart contained in that chart widget
                for chart in w.charts:
                    # update visibility based on selector widget value
                    chart.set_visibility(True if chart.chart_type == self.selector_widget.value else False)
                    chart.update()
            # for each browse on the screen
            for b in self.browse_widgets:
                # hide if selector is not 'browse'
                b.grid.set_visibility(True if self.selector_widget.value == 'browse' else False)

    async def update_report(self, force_update=True):
        """
        asynchronous function for updating the data on screen to match the data on the endpoint,
        with an optional param to force the api to also update it's data
        if force_update is false, the data will be fetched, but the endpoint will not run a query
        """
        # TODO - Determine a way to use this code to generate multiple types of graphs (e.g. Combined Board Tests Per Plant) - see implementation
        # TODO - Should payload include 'force-update'?
        if force_update:
            ui.notify("Update Data at the redis endpoint")
            self.payload = self.payload  # todo: add flag to update the redis data
            # Write code to cache to redis

        ui.notify("Updating graph data")
        # results expected to be a list of objects [{}]
        # as this task is IO heavy, and asynchronous and run by another async system it must be awaited in the main thread to prevent bugs
        results = await run.io_bound(app.connection_manager.GetConnection, endpoint=self.endpoint, payload=self.payload)
        ui.notify(results["status"] + " | " + results["message"])
        data = results["data"]

        # Loop through all browse widgets
        for browse in self.browse_widgets:
            # Update data on each browse
            browse.update_data(data)

        # Loop through all chart widgets
        for i, chart in enumerate(self.chart_widgets):
            # Update data on each chart
            chart.update_data(data, self.chart_configs[i]['graph_attrs'][0], self.chart_configs[i]['graph_attrs'][1])
        # todo: I believe this dt should be kept in redis to identify when the endpoint's data was last updated
        # Update the last updated text
        now_datetime = datetime.now()
        self.last_updated = now_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.update_button.text = f"Last Updated - {self.last_updated if self.last_updated != '' else 'Unknown'} Update Now"
        ui.notify('Graph Data Updated')

    def selector_widget_changed(self, event):
        """ event called from the selector widget's value change event, call the actual function from here """
        self.selected_widget_changed()

    def selected_widget_changed(self):
        """ the actual function updating the screen """
        for w in self.chart_widgets:
            for chart in w.charts:
                chart.set_visibility(False if chart.chart_type != self.selector_widget.value else True)
                chart.update()

        for b in self.browse_widgets:
            b.grid.set_visibility(False if self.selector_widget.value != 'browse' else True)
