from nicegui import ui

from components.object_views.CombinedTestEntryOrderView import CombinedTestEntryOrderView
from components.object_views.CombinedTestEntryTestView import CombinedTestEntryTestView
from components.object_views.PaperTestEntryRollView import PaperTestEntryRollView
from components.object_views.PaperTestEntryTestView import PaperTestEntryTestView
from components.panels.content_panels.TestEntryBaseContentPanel import TestEntryContentPanel
from components.panels.test_entry_forms.combined.CombinedTestEntryForm import CombinedTestEntryForm
from components.panels.test_entry_forms.paper.PaperTestEntryForm import PaperTestEntryForm
from data_objects.TestEntryScreenData import CombinedTestEntryScreenData, PaperTestEntryScreenData

from pages.NiceKTCPage import NiceKTCPage


class CombinedTestEntryScreen(NiceKTCPage):
    def __init__(self):
        super().__init__()
        with self:

            combined_screen = TestEntryContentPanel(title="Combined Board Test Entry", screen="combined")
            # Initialize screen data specific to Paper Test Entry
            combined_screen.screen_data = CombinedTestEntryScreenData()
            # Assign the specific views and form to the page
            combined_screen.selected_view = CombinedTestEntryOrderView
            combined_screen.test_view = CombinedTestEntryTestView
            combined_screen.test_entry_panel = CombinedTestEntryForm
            combined_screen.CreateScreen()



class PaperTestEntryScreen(NiceKTCPage):
    def __init__(self):
        super().__init__()
        with self:
            paper_screen = TestEntryContentPanel(title="Paper Test Entry", screen="paper")
            # Initialize screen data specific to Paper Test Entry
            paper_screen.screen_data = PaperTestEntryScreenData()
            # Assign the specific views and form to the page
            paper_screen.selected_view = PaperTestEntryRollView
            paper_screen.test_view = PaperTestEntryTestView
            paper_screen.test_entry_panel = PaperTestEntryForm
            paper_screen.CreateScreen()

