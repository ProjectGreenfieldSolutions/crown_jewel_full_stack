from nicegui import ui, app



class DjangoDropdown(ui.select):
    """
    parent class for dropdowns populated form django util_api, util_api initialized on app startup
    """
    action = ""
    label = ""

    def __init__(self, bind_tuple=None, value=''):
        self.init_value = value
        app.logger.debug(message=f"Initialization {self.action}", details="DjangoDropdown")
        response = app.connection_manager.GetConnection(endpoint="/util", payload={"action": self.action, "plant_code": app.storage.user.get('plant')})
        self.options = {"":""}

        if response:
            app.logger.debug(message=f"response={response}", details="DjangoDropdown")
            for key in response:
                # logger.debug(message=f"key={key}", details="DjangoDropdown")
                self.options[key] = response[key]
        else:
            app.logger.warning(message=f"No response", details="DjangoDropdown")
            self.options['0'] = 'failed to fetch options'
        super().__init__(label=self.label, options=self.options, value = self.init_value)
        with self:
            if bind_tuple is not None:
                self.bind_value(bind_tuple[0], bind_tuple[1])
                self.value = self.init_value



class AuthorDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = 'Authors:'
        self.action = 'accounts'
        super().__init__(bind_tuple)


class PaperTestTypeDropDown(DjangoDropdown):
    def __init__(self, bind_tuple, value=''):
        self.label = 'Type:'
        self.action = 'paper_test_types'
        super().__init__(bind_tuple, value=value)


class CombinedBoardTestTypeDropDown(DjangoDropdown):
    def __init__(self, bind_tuple, value=''):
        self.label = 'Type:'
        self.action = "combined_board_test_types"
        super().__init__(bind_tuple, value)


class VendorDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Vendor:"
        self.action = "vendors"
        super().__init__(bind_tuple)


class GradeDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Grade:"
        self.action = "grades"
        super().__init__(bind_tuple)


class PlantDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Plant:"
        self.action = "plants"
        super().__init__(bind_tuple)


class CombinedBoardTestReasonDropDown(DjangoDropdown):
    def __init__(self, bind_tuple, value=''):
        self.label = "Reason:"
        self.action = "combined_board_test_reasons"
        super().__init__(bind_tuple, value=value)


class PaperTestReasonDropDown(DjangoDropdown):
    def __init__(self, bind_tuple, value=''):
        self.label = "Reason:"
        self.action = "paper_test_reasons"
        super().__init__(bind_tuple, value=value)


class PaperTestPositionDropDown(DjangoDropdown):
    def __init__(self, bind_tuple, value=''):
        self.label = "Test(s) Position:"
        self.action = "paper_test_positions"
        super().__init__(bind_tuple, value=value)


class PaperTypeDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Type:"
        self.action = "paper_types"
        super().__init__(bind_tuple)


class CustomersDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Customer:"
        self.action = "customers"
        super().__init__(bind_tuple)


class CorrugatorsDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Corrugator:"
        self.action = "corrugators"
        super().__init__(bind_tuple)


class LithosDropDown(DjangoDropdown):
    def __init__(self, bind_tuple, value=''):
        self.label = "Litho:"
        self.action = "lithos"
        super().__init__(bind_tuple, value=value)


class FlutesDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Flute:"
        self.action = "flutes"
        super().__init__(bind_tuple)


class OrderTestCodeDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Test Code:"
        self.action = "order_test_codes"
        super().__init__(bind_tuple)


class SpecInstrCodeDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Special Instructions:"
        self.action = "special_instruction_codes"
        super().__init__(bind_tuple)


class CombinedBoardTestLayerDropDown(DjangoDropdown):
    def __init__(self, bind_tuple):
        self.label = "Layer:"
        self.action = "combined_board_test_layers"
        super().__init__(bind_tuple)
