from components.charts.piecharts.PieChart import PieChart
from nicegui import app

class PaperTestsPieChart(PieChart):
  def __init__(self):
    super().__init__(title="Paper Tests", data=app.util_api.FetchPaperTestPieChartValues())

