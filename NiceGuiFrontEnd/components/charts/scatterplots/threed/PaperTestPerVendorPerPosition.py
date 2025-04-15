from components.charts.scatterplots.threed.ThreeDScatterPlot import ThreeDScatterPlot


class PaperTestPerVendorPerPosition(ThreeDScatterPlot):
  def __init__(self, vendors, positions, test_averages):
    super().__init__(title='Test Averages per Position per Vendor', x_label='Vendors', x_values=vendors,
                     y_label='Positions', y_values=positions,
                     z_label='Test Averages', z_values=test_averages)