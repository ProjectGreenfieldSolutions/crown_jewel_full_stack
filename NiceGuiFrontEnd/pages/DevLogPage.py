from nicegui import app, ui
import json

from pages.NiceKTCPage import NiceKTCPage


class DevLogPage(NiceKTCPage):
    def __init__(self):
        super().__init__()
        with self.classes('w-full'):
            self.page_header()
            self.build_dev_log_panel()

    @staticmethod
    def set_card_title(title):
        return ui.label(title).classes("place-self-center")

    @staticmethod
    def set_card_body(devlog):
        return ui.markdown(devlog).classes("place-self-center")

    def page_header(self):
        with ui.grid(columns=1).classes("w-full"):
            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log important notice")
                ui.separator()
                self.set_card_body(devlog="""
                * Note: This isn't representative of every single little update performed on this project.
                * Merely this is an attempt to catalogue the overview components that have change. 
                """)

    def build_dev_log_panel(self):
        with ui.grid(columns=1).classes("w-full"):
            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log version 1.06")
                ui.separator()
                self.set_card_body(devlog="""
                * Combined Board Tests
                    * Included the liners AND mediums in the export
                    * Changed all column headers to UPPERCASE
                    * Putting Litho values in each of the ROLL columns
                    * Fixed the funky date column value
                    * Removed that weird last row record that was being created
                        * Need feedback but 90% this is fixed
                    * Believe the failure to print Litho records is resolved
                        * Need feedback as I couldn't easily find an order to test this on
                """)

            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log version 1.05")
                ui.separator()
                self.set_card_body(devlog="""
                * Combined Board Tests
                    * Enhanced order no filter
                        * No need to do an exact copy to filter records
                    * Completely changed the format that the database sends results back to the front end
                        * Shows each test value individually on the web page
                        * Combines all the test values, for matching order no's on the exports (CSV / Excel)
                * Paper Tests
                    * Enhanced roll no filter
                        * No need to do an exact copy to filter records
                """)

            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log version 1.04")
                ui.separator()
                self.set_card_body(devlog="""
                * Auto logout mechanism
                    * System is set to log the user out after 15 minutes of inactivity.
                    * Once 15 minutes of inactivity occurs, system will prompt the user with a pop-up with a 10 second warning
                * Paper Tests / Combined Board Tests
                    * Date range now works as expected
                    * Included a column of "Created" to better display when the record was created
                    * Introduced a new pop-up message for when records aren't found using the filters
                * Combined Board Test Entry
                    * Roll verification on the Combined Board Test Entry screen now clears when test entries are submitted
                    * Included programming to prevent double submissions of test entries if the button is double clicked
                """)

            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log version 1.03")
                ui.separator()
                self.set_card_body(devlog="""
                * Added new web page called "Dev Log" 
                * Refactored the restore from database backup script. 
                    * Now will make multiple attempts in the event of a failure.
                * Included additional logic in the setup procedures
                    * Files that may have been accidental converted to windows format (CRLF) will get converted back to unix format (LF)
                * Enabled navigation to the Modifications screen
                * Reworked the Modifications screen to be more user friendly
                    * "code" is the key that binds the "description" to itself. Most of the drop-downs in the system display "description"... however code in the background uses "code" to search/index data. 
                    * If you type in "10pt" in the "code" field, the green "add new records" button will change to "update" indicating that you're matching an existing record. Good visual cue that you're in fact updating and not adding a new record.
                    * "Start Over" just refreshes the page. 
                    * Notes:
                        * This screen ONLY will **add** or **update** records
                        * No delete is allowed as database tables are tightly coupled together
                        * This means you must contact KTC to delete records that are keyed in here
                * Wrote a huge amount of documentation for developers that get involved in this project
                """)

            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log version 1.02")
                ui.separator()
                self.set_card_body(devlog="""
                * Added Quality Issue to Paper Test Entry Reason selection drop-down
                * User preferences will now actually save your settings
                * Performed a massive facelift of the User Preferences screen
                * Added the ability to select the default testing types for Paper Test Entry / Combined Test Entry into the User Preferences
                * Added Default # of layers, Default # of tests upon page load for their respective screens
                * Removed roll verification from Paper Test Entry
                * Removed the bug that overwrote the user preferences the users session previously had upon logging in
                * Resolved runtime error when a brand new user preference is added to an account
                """)

            with ui.card().classes("place-self-center w-3/4"):
                self.set_card_title(title="Dev log version 1.01")
                ui.separator()
                self.set_card_body(devlog="""
                * Refactor of the generation for paper tests report (UI / Export)
                * Inclusion of omission of financial data if not a supervisor account
                * Integrated Jays Dashboard changes
                    * Included Jays ReportBrowse for dashboard stuff
                	* Included Jays ReportPanel for dashboard stuff
                	* Included Jays MultiChart to display users selected chart using the same dataset
                * Inclusion of the refactored, wip, modifications screen
                * Added additional endpoints for modifications / dashboard queries
                * Made the Django Debugging global to easily show built-in Django error messages
                * Updated logging with documentation
                * Updated code in the DjangoWebOLV to handle the changed Paper Tests display
                * Moved the asynchronuous calls to be uniform throughout the application (was two different type)
                * Added drop-down list to the login screen
                * Integrated the refactor for the Modifications screen
                * Added some QoL messages to the Paper Tests
                * Included documentation to shell scripts
                * Bumped up the maximum allowed ram to 200M
                * Updated readme with more information about the project
                """)
