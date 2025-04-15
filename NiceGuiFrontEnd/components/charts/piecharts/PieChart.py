from nicegui import ui

class PieChart(ui.highchart):
    def __init__(self, title='Lorem ipsum', data=[['lorem ipsum', 15], ['ipsum lorem', 40]]):
        super().__init__({
            'title': {'text': title},
            'chart': {'type': 'pie'},  # Change the chart type to 'pie'
            'series': [
                {'name': 'Test per plant', 'data': data},  # Adjust data format for pie chart
            ],
            'plotOptions': {
                'pie': {
                    'startAngle': -90
                }
            },
            'credits': False, # Removes the hyperlink to Highcharts.com
        })
        with self:
            self.classes('w-full h-full')