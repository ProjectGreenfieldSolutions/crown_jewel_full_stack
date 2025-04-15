import plotly.graph_objs as go
from nicegui import ui


class ThreeDScatterPlot:
  def __init__(self, title, x_label, x_values, y_label, y_values, z_label, z_values):
    # Create the Plotly figure
    fig = go.Figure(data=[go.Scatter3d(
      x=x_values,
      y=y_values,
      z=z_values,
      mode='markers',
      marker=dict(
        size=5,
        color=z_values,
        colorscale='Viridis',
        opacity=0.8
      )
    )])

    fig.update_layout(
      title=title,
      scene=dict(
        xaxis_title=x_label,
        yaxis_title=y_label,
        zaxis_title=z_label
      ),
    width=1200,  # Set the desired width
    height=700  # Set the desired height
    )

    # Convert figure to HTML content
    ui.plotly(fig).classes('w-full h-full')