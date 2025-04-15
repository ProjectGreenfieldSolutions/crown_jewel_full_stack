""" object housing on screen widgets for the paper test page """
from nicegui import ui, app
from pages.NiceKTCPage import NiceKTCPage


class TablePage(NiceKTCPage):
    def __init__(self):
      super().__init__()
      with self:
        self.PROGRESS_TABLES = ["plant", "vendor", "grade", "customer", "corrugator", "flute", "paper_type",
                                "order_test_code"]
        self.DJANGO_TABLES = ["account", "litho", "special_instruction_code", "paper_test_reason",
                              "paper_test_position",
                              "paper_test_type", "combined_board_test_reason", "combined_board_test_layer",
                              "combined_board_test_type"]
        with ui.grid(columns=3).classes("w-full"):
            for table in self.PROGRESS_TABLES:
                with ui.card():
                    ui.label(f"{self.format_table_name(table)} TABLE")
                    ui.separator()
                    ui.button(f"Show ({app.storage.user.get('plant')}) {self.format_table_name(table)} records",
                              on_click=lambda t=table: self.display_results(
                                  app.connection_manager.GetConnection(endpoint="/util",
                                                                       payload={"action": f"{t}s",
                                                                                "plant_code": app.storage.user.get(
                                                                                    "plant")}))
                              ).classes("w-full")
                    ui.button(f"Sync ({app.storage.user.get('plant')}) {self.format_table_name(table)} records",
                              on_click=lambda t=table: self.display_results(
                                  app.connection_manager.GetConnection(endpoint="/util",
                                                                       payload={"action": f"{t}s",
                                                                                "plant_code": app.storage.user.get(
                                                                                    "plant"),
                                                                                "update": True}))
                              ).classes("w-full").props("color=red")

        with ui.grid(columns=3).classes("w-full"):
            for index, table in enumerate(self.DJANGO_TABLES):
                with ui.card():
                    ui.label(f"{self.format_table_name(table)} TABLE")
                    ui.button(f"Show ({app.storage.user.get('plant')}) {self.format_table_name(table)}",
                              on_click=lambda t=table: self.display_results(
                                  app.connection_manager.GetConnection(endpoint="/util",
                                                                       payload={"action": f"{t}s",
                                                                                "plant_code": app.storage.user.get(
                                                                                    "plant")
                                                                                }
                                                                       )
                              ))
        with ui.grid(columns=3).classes("w-full"):
            with ui.card():
                ui.label("SYNC ALL TABLES, ALL PLANTS")
                ui.separator()
                ui.label(
                    "NOTE THAT THIS TAKES A VERY LONG TIME (3 minutes???). YOU WILL SEE A CONNECTION WARNING ON BOTTOM-LEFT. JUST IGNORE IT AND WAIT UNTIL THE PAGE RELOADS.")
                ui.button(f"Sync ALL tables, all plants", on_click=lambda: self.sync_all_tables()).props("color=red")

    def sync_all_tables(self):
        list_of_plants = app.connection_manager.GetConnection(endpoint="/util",
                                                              payload={"action": "plants",
                                                                       "plant_code": app.storage.user.get("plant"),
                                                                       "update": True})
        for code, desc in list_of_plants.items():
            for table in self.PROGRESS_TABLES:
                app.connection_manager.GetConnection(endpoint="/util",
                                                     payload={"action": f"{table}s",
                                                              "plant_code": code,
                                                              "update": True})

    @staticmethod
    def format_table_name(value: str):
        return value.replace("_", " ").upper()

    @staticmethod
    def display_results(results):
        ui.notify(results)
