from components.charts.scatterplots.threed.ThreeDScatterPlot import ThreeDScatterPlot


class CombinedThreeD(ThreeDScatterPlot):
  def __init__(self, vendors, positions, test_averages, test_type):
    title = f'{test_type} Test Averages per Position per Vendor'
    super().__init__(
      title=title,
      x_label='Vendors',
      x_values=vendors,
      y_label='Positions',
      y_values=positions,
      z_label='Test Averages',
      z_values=test_averages
    )