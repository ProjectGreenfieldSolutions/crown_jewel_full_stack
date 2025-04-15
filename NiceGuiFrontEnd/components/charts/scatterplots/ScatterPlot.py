from nicegui import ui

class ScatterPlot:
  def __init__(self, x_attr, y_attr, objs, splitting_attr='', on_click_callback=None):
      figure_data = []
      if splitting_attr != '':
        splits = self.get_data_splits(objs, splitting_attr)
        for split in splits:
          x_values = []
          y_values = []
          for obj in self.filter_split(objs, split, splitting_attr):
            if obj[splitting_attr] == split:
              x_values.append(obj[x_attr])
              y_values.append(obj[y_attr])
          figure_data.append(
            {
              'type': 'scatter',
              'name': f'{split}',
              'x': x_values,
              'y': y_values,
            })
      else:
        figure_data.append(
          {
            'mode': 'markers',
            'type': 'scatter',
            'name': f'Combined Test Values by Roll Number',
            'x': [x[x_attr] for x in objs],
            'y': [y[y_attr] for y in objs],
          })
      fig = {
        'data': figure_data,
      }
      ui.plotly(fig).classes('w-full h-full').on('plotly_click', lambda msg : on_click_callback(msg))


  def filter_split(self, data, split_name, splitting_attr):
    return_list = []
    for obj in data:
      for k, v in obj.items():
        if v[splitting_attr] == split_name:
          return_list.append(v)
    return return_list

  def get_data_splits(self, data, attr):
    list_of_splits = []
    for obj in data:
      for k, v in obj.items():
        if v[attr] not in list_of_splits:
          list_of_splits.append(v[attr])
    return list_of_splits