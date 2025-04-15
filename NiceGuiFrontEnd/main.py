# import web app class and auth functions
from core.QualityDashApp import QualityDashApp
# import pages used in the app
from pages.ModificationScreenManagerPage import ModificationScreenManagerPage
from pages.PaperTestPage import PaperTestPage
from pages.DashboardPage import DashboardPage
from pages.TestEntryPages import PaperTestEntryScreen, CombinedTestEntryScreen
from pages.CombinedTestPage import CombinedTestPage
from pages.PreferencesPage import PreferencesPage
from pages.DevLogPage import DevLogPage


# Define dictionary of pages to use
pages_dict = {
    "dashboard": {"title": "Dashboard", "page": DashboardPage},
    "paper_tests": {"title": "Paper Tests", "page": PaperTestPage},
    "paper_test_entry": {"title": "Paper Test Entry", "page": PaperTestEntryScreen},
    "combined_tests": {"title": "Combined Tests", "page": CombinedTestPage},
    "combined_test_entry": {"title": "Combined Test Entry", "page": CombinedTestEntryScreen},
    "profile": {"title": "User Preferences", "page": PreferencesPage},
    "modifications": {"title": "Modify App Records", "page": ModificationScreenManagerPage},
    "devlog": {"title": "Dev Logs", "page": DevLogPage},
}

dev_pages = {}
# Keeping for legacy purposes
# from pages.TablePage import TablePage
# dev_pages = {
#     'tables': {'title': 'Test Tables', 'page': TablePage},
# }
#account_api = AccountData()
# initialize app
if __name__ in {"__main__", "__mp_main__"}:
    QualityDashApp('Quality Dash', pages_dict, dev_pages, "QDASH")
