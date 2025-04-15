from datetime import datetime

import plotly.graph_objects as go
from nicegui import ui, app

# Mapping categories to numeric values for scatter and line charts
# TODO: implement generic encoding method
category_to_numeric = {"MS": 0, "OP": 1, "CC": 2, "SP": 3, "MC": 4, "PA": 5}




class DynamicChart(ui.plotly):
  def __init__(self, title='', chart_type='bar'):
    self.chart_type = chart_type
    self.title = title
    self.data = None

    self.original_colors = ["#ff9999", "#66b3ff", "#99ff99",
                            "#ffcc99", "#c2c2f0", "#ffb3e6"]

    # Map chart types to Plotly graph objects
    chart_type_mapping = {
      'pie': go.Pie,
      'bar': go.Bar,
      'scatter': go.Scatter,
      'line': go.Scatter,  # Line charts use Scatter with mode='lines'
    }

    self.figure_method = chart_type_mapping.get(self.chart_type, go.Scatter)

    # Initialize the figure based on the chart type
    self.init_figure()

    # Set uirevision to preserve zoom and selection
    self.fig.update_layout(
      title=self.title,
      uirevision='constant',
    )

    # Render the UI components
    with ui.element('div') as self.container:
      super().__init__(self.fig)

      # Bind hover and unhover events
      self.on("plotly_hover", self.on_hover)
      self.on("plotly_unhover", self.on_unhover)

  def init_figure(self):
    data = self.data
    if data is None:
      data = {'x': [], 'y': []}
    if self.chart_type == 'pie':
      labels = data.get('labels', data.get('x'))
      values = data.get('values', data.get('y'))
      marker = dict(colors=self.original_colors)
      self.fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, marker=marker)])
      # Initialize pull values
      self.fig.data[0].pull = [0] * len(labels)
    else:
      x_categories = data.get('x', [])
      y = data.get('y', [])
      marker = dict(color=self.original_colors)

      if self.chart_type == 'line' or self.chart_type == 'scatter':
        x = [category_to_numeric.get(cat, idx) for idx, cat in enumerate(x_categories)]
        mode = 'lines+markers' if self.chart_type == 'line' else 'markers'
        self.fig = go.Figure(data=[self.figure_method(x=x, y=y, mode=mode, marker=marker)])
        # Update x-axis tick labels to display categories
        self.fig.update_layout(
          xaxis=dict(
            tickmode='array',
            tickvals=x,
            ticktext=x_categories
          )
        )
      elif self.chart_type == 'bar':
        x = x_categories  # Use categories directly
        self.fig = go.Figure(data=[go.Bar(x=x, y=y, marker=marker)])
        # Explicitly set x-axis type to 'category'
        self.fig.update_layout(
          xaxis=dict(
            type='category'
          )
        )
      else:
        # Handle other chart types if necessary
        pass

  def update_data(self, data):
    self.data = data
    if self.chart_type == 'pie':
      labels = data.get('labels', data.get('x'))
      values = data.get('values', data.get('y'))
      self.fig.data[0].labels = labels
      self.fig.data[0].values = values
      self.fig.data[0].marker.colors = self.original_colors
      # Reset pull values
      self.fig.data[0].pull = [0] * len(labels)
    else:
      x_categories = data.get('x')
      y = data.get('y')
      self.original_colors = data.get('colors', self.original_colors)

      if self.chart_type == 'line' or self.chart_type == 'scatter':
        #todo: this needs to be a more generic method of encoding
        x = [category_to_numeric.get(cat, idx) for idx, cat in enumerate(x_categories)]
        self.fig.data[0].x = x
        self.fig.data[0].y = y
        self.fig.data[0].marker.color = self.original_colors
        # Update x-axis tick labels to display categories
        self.fig.update_layout(
          xaxis=dict(
            tickmode='array',
            tickvals=x,
            ticktext=x_categories
          )
        )
      elif self.chart_type == 'bar':
        x = x_categories  # Use categories directly
        self.fig.data[0].x = x
        self.fig.data[0].y = y
        self.fig.data[0].marker.color = self.original_colors
        # Ensure x-axis type remains 'category' after update
        self.fig.update_layout(
          xaxis=dict(
            type='category'
          )
        )
      else:
        # Handle other chart types if necessary
        pass

    # Update the figure without resetting user interactions
    self.update()

  def on_hover(self, event):
    event_data = event.args
    if 'points' in event_data and event_data['points']:
      point = event_data['points'][0]
      point_index = point.get('pointNumber', 0)

      if self.chart_type == 'pie':
        # Update the pull value for the hovered slice
        pull_values = [0] * len(self.fig.data[0].labels)
        pull_values[point_index] = 0.1  # Pull out the hovered slice
        self.fig.data[0].pull = pull_values
      else:
        # Update the marker color for the hovered point
        colors = self.original_colors.copy()
        colors[point_index] = 'gold'  # Highlight the hovered point
        self.fig.data[0].marker.color = colors
      # Update the figure without resetting user interactions
      self.update()

  def on_unhover(self, event):
    if self.chart_type == 'pie':
      # Reset pull values
      self.fig.data[0].pull = [0] * len(self.fig.data[0].labels)
    else:
      # Reset marker colors
      self.fig.data[0].marker.color = self.original_colors
    # Update the figure without resetting user interactions
    self.update()

  # Method to show or hide the chart (not used in this implementation)
  def set_visibility(self, visible):
    self.container.style('display: block;' if visible else 'display: none;')


class MultiChart:
  def __init__(self, title="Dynamic Chart", charts_to_show=None):
    if charts_to_show:
      self.charts_to_show = charts_to_show
    else:
      self.charts_to_show = ['bar', 'scatter', 'line', 'pie']

    self.title = title
    ui.label(self.title)
    # Display the charts in a 2x2 grid
    if self.charts_to_show is not None:
      self.charts = [
        DynamicChart(
          title=f'{self.title} Bar Chart',
          chart_type='bar',
        ) if 'bar' in self.charts_to_show else None,
        DynamicChart(
          title=f'{self.title} Scatter Plot',
          chart_type='scatter',
        ) if 'scatter' in self.charts_to_show else None,
        DynamicChart(
          title=f'{self.title} Line Chart',
          chart_type='line',
        ) if 'line' in self.charts_to_show else None,
        DynamicChart(
          title=f'{self.title} Pie Chart',
          chart_type='pie',
        ) if 'pie' in self.charts_to_show else None,
      ]


  def update_data(self, data, x_attr, y_attr):
    # Fetch updated data once
    self.data = self.format_updata_data(data, x_attr, y_attr)  # Update stored data
    # Update all charts
    for chart in self.charts:
      if chart is not None:
        chart.update_data(self.data)


  def format_updata_data(self, data, x_attr, y_attr):
    data = data
    figure_data = {}
    figure_data["x"] = [x[x_attr] for x in data]
    figure_data["y"] = [x[y_attr] for x in data]
    return figure_data


