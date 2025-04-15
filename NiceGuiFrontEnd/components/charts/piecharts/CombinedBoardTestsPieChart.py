from components.charts.piecharts.PieChart import PieChart
from nicegui import app

class CombinedBoardTestsPieChart(PieChart):
  def __init__(self):
    super().__init__(title="Combined Board Tests", data=app.util_api.FetchCombinedTestPieChartValues())
