"""
panel for filtering and searching paper tests
"""
from .FilterPanelBase import FilterPanelBase
from nicegui import app

class FilterPaperTests(FilterPanelBase):
    """
    subclassed from the filter screen base, this creates the filter grid for searching paper test
    """
    def __init__(self, parent):
        title = "Filter Paper Tests"
        #if you add to this, you must also set it in preferences page
        filter_dict = {}
        for filter, options in app.paper_test_default_filters.items():
            if options['title'][:-1] in app.storage.user.get("preferences")['page_settings']['paper_tests']['filter_attributes']:
                filter_dict[filter] = options
        super().__init__(parent, title, filter_dict)
