""" A Browse like widget for the report panel """
# nicegui library imports
from nicegui import ui, run, app


class ReportBrowse:
  """
  in the erp or shipping this would be called an OLV, this is a browse widget for dynamically displaying the objects
  visualized by a report panel
  init_data is optional and should be a list of objects to be displayed if being used
  """
  def __init__(self, title='', init_data=None):
    objects = init_data

    ui.label(f'{title}')

    # Define the grid with column definitions and empty initial data
    self.grid = ui.aggrid(
      options={
        "columnDefs": [{"headerName": key, "field": key} for key in
                       objects[0].keys()] if init_data is not None else None,
        "rowData": init_data if init_data is not None else None,
        "defaultColDef": {"resizable": True, "sortable": True, 'filter': True},
        "pagination": True,
      }
    )

  def update_data(self, data):
    """ Updates the grid data with new objects """
    ## Column definitions
    self.grid.options["columnDefs"] = [{"headerName": key, "field": key} for key in
                                       data[0].keys()] if data is not None else None
    ## Row data
    self.grid.options["rowData"] = data
    ## Column options
    self.grid.options["defaultColDef"] = {"resizable": True, "sortable": True, 'filter': True}
    ## Pagination
    self.grid.options["pagination"] = True
    ## Update UI widget
    self.grid.update()
