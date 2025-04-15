from .FilterPanelBase import FilterPanelBase
from nicegui import app

class FilterCombinedTests(FilterPanelBase):
    """
    subclassed from the filter screen base, this creates the filter grid for searching combined test
    """
    def __init__(self, parent):
        title = "Filter Combined Tests"
        filter_dict = {}
        for filter, options in app.combined_test_filter_defaults.items():
            if options['title'][:-1] in app.storage.user.get("preferences")['page_settings']['combined_tests']['filter_attributes']:
                filter_dict[filter] = options
        super().__init__(parent, title, filter_dict)

