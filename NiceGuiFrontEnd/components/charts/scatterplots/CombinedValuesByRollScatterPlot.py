from components.charts.scatterplots.ScatterPlot import ScatterPlot


class CombinedValuesByRollScatterPlot(ScatterPlot):
  def __init__(self, objs):
    super().__init__(x_attr='Roll Number',y_attr='Test Value',objs=objs)