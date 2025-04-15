""" base page to inherit all pages from for the ktc framework """
from nicegui import ui, app

class NiceKTCPage(ui.card):
  def __init__(self):
    super().__init__()
    self.classes('w-full')

  def CallBefore(self):
    """
    Called from the app level, this is fired before screen rendering, useful for preloading
    """
    app.logger.info('Called Before')

  async def CallAfter(self):
    """
    Called from the app level, this is fired after screen rendering, useful for postloading
    """
    app.logger.info("Called After")