from django.urls import path, include
from .views.authentication import Authenticate, Login, Logout, Registration
from .views.account import InitAccount, UpdatePreferences, GetAccountData, UpdateAccountData
from .views.combined import FetchCombinedTests, FetchCombinedTestEntries, CombinedSearchOrder
from .views.paper import FetchPaperTests, FetchRollPaperTestEntries, FetchLithoPaperTestEntries, PaperSearchRoll, PaperSearchLitho
from .views.utilities import CommitTestEntryData, UtilityData, DeleteTestEntry, ModifyEntry, RollVerification, FetchTargetModel
from .views.dashboard import DashboardData

urlpatterns = [
    # Authentication / User stuff
    path('accounts/login', Login, name="account_login"),
    path('accounts/registration', Registration, name="account_registration"),
    path('accounts/logout', Logout, name="account_logout"),
    path("authentication", Authenticate, name="authenticate_progress"),
    path("init_account", InitAccount, name="initialize_account"),
    path("update_preferences", UpdatePreferences, name="update_preferences"),
    path('get_accounts', GetAccountData, name="get_account_data"),
    path('update_accounts', UpdateAccountData, name="update_account_data"),

    # Combined
    path('combined/fetch_tests', FetchCombinedTests, name="combined_test"),
    path('combined/fetch_test_entries', FetchCombinedTestEntries, name="fetch_combined_test_entries"),
    path('combined/search_order', CombinedSearchOrder, name="combined_search_order"),
    # path('combined/test_entry', CombinedTestEntry, name="combined_test_entry"),

    # Paper
    path('paper/fetch_tests', FetchPaperTests, name="fetch_paper_tests"),
    path('paper/fetch_roll_test_entries', FetchRollPaperTestEntries, name="fetch_roll_paper_test_entries"),
    path('paper/fetch_litho_test_entries', FetchLithoPaperTestEntries, name="fetch_litho_paper_test_entries"),
    path('paper/search_roll', PaperSearchRoll, name="paper_search_roll"),
    path('paper/search_litho', PaperSearchLitho, name="paper_search_litho"),
    # path('paper/test_entry', PaperTestEntry, name="paper_test_entry"),

    # Utility
    path('util', UtilityData, name="get_utility_data"),
    path("dashboard", DashboardData, name="dashboard_data"),
    path("modify_entry", ModifyEntry, name="modify_entry"),
    path("roll_verification", RollVerification, name="roll_verification"),
    path("fetch_model", FetchTargetModel, name="fetch_entire_model"),

    # Commit Test Entry Data
    path('commit', CommitTestEntryData, name="commit_test_entry_data"),

    # Delete Test Entry Data
    path('delete', DeleteTestEntry, name="delete_test_entry_data"),
]