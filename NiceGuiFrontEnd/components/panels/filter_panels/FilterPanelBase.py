from nicegui import ui
from components.widgets.DropDownWidgets import PlantDropDown, AuthorDropDown, GradeDropDown, PaperTypeDropDown, FlutesDropDown, CombinedBoardTestTypeDropDown


class FilterPanelBase:
  def __init__(self, parent, title="Title", filter_dict=None):
    if filter_dict is None:
      filter_dict = {"attr_name": {'title': 'Label:', 'type': 'string'}}

    self.parent = parent
    self.screen_data = self.parent.screen_data  # Input declarations
    self.filter_dict = filter_dict
    self.filter_grid = ui.grid(columns=len(filter_dict.keys())).classes('w-full')

    with self.filter_grid:
      ui.label(f"{title}").classes("col-span-full")
      ui.separator().classes("col-span-full")
      for k in self.filter_dict.keys():
        t_type = self.filter_dict[k].get('type')
        if t_type == 'string':
          ui.input(label=self.filter_dict[k].get('title')).bind_value(self.screen_data, k)
        elif t_type == 'date':
          with ui.input(label=self.filter_dict[k].get('title')).bind_value(self.screen_data, k) as date:
            with ui.menu().props('no-parent-event') as menu:
              with ui.date().bind_value(date):
                with ui.row().classes('justify-end'):
                  ui.button('Close', on_click=menu.close).props('flat')
            with date.add_slot('append'):
              ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
        elif t_type == 'int':
          ui.number(label=self.filter_dict[k].get('title')).bind_value(self.screen_data, k)
        elif t_type == 'plant':
          PlantDropDown(bind_tuple=(self.screen_data, k))
        elif t_type == 'account':
          AuthorDropDown(bind_tuple=(self.screen_data, k))
        elif t_type == 'grade':
          GradeDropDown(bind_tuple=(self.screen_data, k))
        elif t_type == 'paper_type':
          PaperTypeDropDown(bind_tuple=(self.screen_data, k))
        elif t_type == 'flute':
          FlutesDropDown(bind_tuple=(self.screen_data, k))
        elif t_type == 'combined_test_type':
          CombinedBoardTestTypeDropDown(bind_tuple=(self.screen_data, k))

      ui.button("Search").classes("col-span-full").on_click(self.submit)

  def submit(self):
    """ calls populate in the page main panel """
    self.parent.populate()
