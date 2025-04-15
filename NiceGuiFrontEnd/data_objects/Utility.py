from nicegui import ui, app
import asyncio


class UtilityData:
    def __init__(self):
        app.logger.info(f"UtilityData class has been initialized")
        self.plant_code_dict = {}
        self.author_dict = {}
        self.grade_dict = {}
        self.paper_type_dict = {}
        self.results = {}
        self.updating = False

    @staticmethod
    def MakeConnection(endpoint, payload):
        display = app.connection.GetConnection(endpoint=endpoint, payload=payload)
        ui.notify(display)
        return display

    async def FetchPlantCodes(self) -> None:
        app.logger.info(f"Attempting to fetch plant code records")
        endpoint = "/util"
        payload = {"action": "plants", "plant_code": app.storage.user.get("plant")}
        results = self.MakeConnection(endpoint=endpoint, payload=payload)
        if results:
            self.results = results
            app.logger.info(f"Fetched plant code records")
            ui.notify(f"PlantCodes={results}")
            self.UpdatePlantCodes()
        else:
            error_message = f"Error - Failed to fetch plant code records"
            app.logger.error(error_message)

    def UpdatePlantCodes(self):
        app.logger.info(f"Updating the dictionary that holds plant code information")
        app.logger.debug(f"self.results = {self.results}")
        for key, value in self.results.items():
            self.plant_code_dict[key] = value
        app.logger.debug(f"Dictionary updated = {self.plant_code_dict}")

    async def FetchPaperTypes(self) -> None:
        app.logger.info(f"Attempting to fetch type code records")
        endpoint = "/util"
        payload = {"action": "paper_types", "plant_code": app.storage.user.get('location')}
        results = self.MakeConnection(endpoint=endpoint, payload=payload)
        app.logger.debug(message=f"results={results}", details=f"FetchTypeCodes")
        if results:
            self.results = results
            app.logger.info(f"Fetched type code records")
            ui.notify(f"PaperTypeCodes={results}")
            self.UpdatePaperTypes()
        else:
            error_message = f"Error - Failed to fetch type code records"
            app.logger.error(error_message)

    def UpdatePaperTypes(self):
        app.logger.info(f"Updating the dictionary that holds type code information")
        app.logger.info(self.results)
        for key, value in self.results.items():
            self.plant_code_dict[key] = value
        app.logger.debug(f"Dictionary updated = {self.paper_type_dict}")

    async def FetchGrades(self) -> None:
        app.logger.info(f"Attempting to fetch grades records")
        endpoint = "/util"
        payload = {"action": "grades", "plant_code": app.storage.user.get("plant")}
        results = self.MakeConnection(endpoint=endpoint, payload=payload)
        if results:
            self.results = results
            app.logger.info(f"Fetched grades records")
            ui.notify(f"Grades={results}")
            self.UpdateGrades()
        else:
            error_message = f"Error - Failed to fetch grade records"
            app.logger.error(error_message)

    def UpdateGrades(self):
        app.logger.info(f"Updating the dictionary that holds grade information")
        app.logger.debug(self.results)
        for key, value in self.results.items():
            self.grade_dict[key] = value
        app.logger.debug(f"Dictionary updated = {self.grade_dict}")

    async def FetchAuthors(self) -> None:
        app.logger.info(f"Attempting to fetch author records")
        endpoint = "/util"
        payload = {"action": "accounts", "plant_code": app.storage.user.get("plant")}
        results = self.MakeConnection(endpoint=endpoint, payload=payload)
        if results:
            self.results = results
            app.logger.info(f"Fetched author records")
            app.logger.debug(message=f"Author records {self.results}")
            ui.notify(message=f"Authors={self.results}")
            self.UpdateAuthors()
        else:
            error_message = f"Error - Failed to fetch author records"
            app.logger.error(error_message)

    def UpdateAuthors(self):
        app.logger.info(f"Updating the dictionary that holds author information")
        for key, value in self.results.items():
            self.author_dict[key] = value
        app.logger.info(message=f"Dictionary updated")
        app.logger.debug(message=f"author_dict={self.author_dict}")

    def PrintValues(self):
        # ui.notify(self.plant_code_dict)
        # ui.notify(self.author_dict)
        # ui.notify(self.grade_dict)
        # ui.notify(self.type_dict)
        pass

    async def HandleNewUserConnection(self):
        if not self.updating:
            self.updating = True
            await asyncio.gather(
                self.FetchPlantCodes(),
                self.FetchPaperTypes(),
                self.FetchGrades(),
                self.FetchAuthors()
            )
            app.logger.info('updated util')
            self.updating = False

    def FetchPaperTestsResults(self, payload):
        results = app.connection_manager.GetConnection(endpoint="/paper/tests", payload=payload)
        results = results['results']
        return_list = []
        for result in results:
            for key, value in result.items():
                if key in payload.keys():
                    if f'{result[key]}'.__contains__(f'{payload[key]}'):
                        return_list.append(result)
        return return_list

    def FetchPaperTestsEntryResults(self, payload):
        """
        Fetch paper test results from the specified API endpoint using the provided payload.

        This function sends a request to the given endpoint with the specified payload and
        returns the results as a list.

        Parameters:
        -----------
        endpoint : str
            The API endpoint to send the request to.
        payload : dict
            The data payload to include in the request, typically containing parameters
            like plant code and roll number.

        Returns:
        --------
        list
            A list containing the results fetched from the endpoint, extracted from the
            dictionary returned by the connection.
        """
        results = app.connection_manager.GetConnection(endpoint="/paper/search_roll", payload=payload)  # Fetch the results from the backend
        return_list = [v for v in results.values()]  # Extract values from the returned dictionary
        return return_list  # Return the list of results

    def FetchCombinedTestsResults(self, payload):
        # results = app.connection_manager.GetConnection(endpoint="/combined/tests", payload={"key1": "value1", "key2": "value2"})
        # results = results['results']
        results = [
            {"id": 0, "order_no": 111111, "plant": "Mason", "test": 32, "flute": "B", "author": "riess",
             "test_type": "ECT",
             "test_reason": "Normal Test", "average": 48.6},
            {"id": 1, "order_no": 222222, "plant": "Mason", "test": 32, "flute": "B", "author": "riess",
             "test_type": "Caliper",
             "test_reason": "Normal Test", "average": 0.121},
            {"id": 2, "order_no": 333333, "plant": "Mason", "test": 32, "flute": "B", "author": "riess",
             "test_type": "Pins DB",
             "test_reason": "Normal Test", "average": 61.9},
            {"id": 3, "order_no": 444444, "plant": "Mason", "test": 32, "flute": "B", "author": "riess",
             "test_type": "Pins MF",
             "test_reason": "Normal Test", "average": 52.7},
        ]
        return_list = []
        for result in results:
            for key, value in result.items():
                if key in payload.keys():
                    if f'{result[key]}'.__contains__(f'{payload[key]}'):
                        return_list.append(result)
        return return_list

    def FetchCombinedTestsEntryResults(self, payload):
        """
        Fetch combined test results from the specified API endpoint using the provided payload.

        This function sends a request to the given endpoint with the specified payload and
        returns the results as a list.

        Parameters:
        -----------
        endpoint : str
            The API endpoint to send the request to.
        payload : dict
            The data payload to include in the request, typically containing parameters
            like plant code and order number.

        Returns:
        --------
        list
            A list containing the fetched results from the endpoint, or an empty list if no results.
        """
        results = app.connection_manager.GetConnection("/combined/search_order", payload)
        return [results] if results else []

    def FetchDashboardCombinedRollTestValues(self):
        # Sample data structured as a dictionary, similar to how it might be in a database
        roll_tests = [
                {'time': '2024-01-01', 'producer': 'Producer A', 'average': 10, 'plant': 'MS'},
                {'time': '2024-02-01', 'producer': 'Producer A', 'average': 15, 'plant': 'OP'},
                {'time': '2024-03-01', 'producer': 'Producer A', 'average': 20, 'plant': 'PA'},
                {'time': '2024-01-01', 'producer': 'Producer B', 'average': 12, 'plant': 'MS'},
                {'time': '2024-02-01', 'producer': 'Producer B', 'average': 18, 'plant': 'OP'},
                {'time': '2024-03-01', 'producer': 'Producer B', 'average': 22, 'plant': 'PA'},
                {'time': '2024-01-01', 'producer': 'Producer C', 'average': 8, 'plant': 'MS'},
                {'time': '2024-02-01', 'producer': 'Producer C', 'average': 14, 'plant': 'OP'},
                {'time': '2024-03-01', 'producer': 'Producer C', 'average': 19, 'plant': 'PA'},
            ]
        producers = [x['producer'] for x in roll_tests]
        plants = [x['plant'] for x in roll_tests]
        averages = [x['average'] for x in roll_tests]
        return producers, plants, averages

    def FetchDashboardCombinedLithoTestValues(self):
        # Sample data structured as a dictionary, similar to how it might be in a database
        litho_tests = [
                {'time': '2024-01-01', 'producer': 'Producer A', 'average': 11, 'plant': 'MS'},
                {'time': '2024-02-01', 'producer': 'Producer A', 'average': 14, 'plant': 'OP'},
                {'time': '2024-03-01', 'producer': 'Producer A', 'average': 18, 'plant': 'PA'},
                {'time': '2024-01-01', 'producer': 'Producer B', 'average': 13, 'plant': 'MS'},
                {'time': '2024-02-01', 'producer': 'Producer B', 'average': 17, 'plant': 'OP'},
                {'time': '2024-03-01', 'producer': 'Producer B', 'average': 20, 'plant': 'PA'},
                {'time': '2024-01-01', 'producer': 'Producer C', 'average': 9, 'plant': 'MS'},
                {'time': '2024-02-01', 'producer': 'Producer C', 'average': 16, 'plant': 'OP'},
                {'time': '2024-03-01', 'producer': 'Producer C', 'average': 21, 'plant': 'PA'},
            ]

        return [x['producer'] for x in litho_tests], [x['plant'] for x in litho_tests], [x['average'] for x in litho_tests]




    def FetchDashboardPaperTestEntries(self):
        test_data = [
            {0: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'inside', 'test_type': 'caliper'}},
            {1: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'inside', 'test_type': 'basis weight'}},
            {2: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'inside', 'test_type': 'brightness'}},
            {3: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'center', 'test_type': 'caliper'}},
            {4: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'center', 'test_type': 'basis weight'}},
            {5: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'center', 'test_type': 'brightness'}},
            {6: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'outside', 'test_type': 'caliper'}},
            {7: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'outside', 'test_type': 'basis weight'}},
            {8: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'outside', 'test_type': 'brightness'}},
            {9: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                 'position': 'inside', 'test_type': 'caliper'}},
            {10: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {11: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'inside', 'test_type': 'brightness'}},
            {12: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'center', 'test_type': 'caliper'}},
            {13: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'center', 'test_type': 'basis weight'}},
            {14: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'center', 'test_type': 'brightness'}},
            {15: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'outside', 'test_type': 'caliper'}},
            {16: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {17: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'outside', 'test_type': 'brightness'}},
            {18: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'inside', 'test_type': 'caliper'}},
            {19: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {20: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'inside', 'test_type': 'brightness'}},
            {21: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'center', 'test_type': 'caliper'}},
            {22: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'center', 'test_type': 'basis weight'}},
            {23: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'center', 'test_type': 'brightness'}},
            {24: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'outside', 'test_type': 'caliper'}},
            {25: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {26: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'outside', 'test_type': 'brightness'}},
            {27: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'inside', 'test_type': 'caliper'}},
            {28: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {29: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'inside', 'test_type': 'brightness'}},
            {30: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'center', 'test_type': 'caliper'}},
            {31: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'center', 'test_type': 'basis weight'}},
            {32: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'center', 'test_type': 'brightness'}},
            {33: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'outside', 'test_type': 'caliper'}},
            {34: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {35: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'outside', 'test_type': 'brightness'}},
            {36: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'inside', 'test_type': 'caliper'}},
            {37: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {38: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'inside', 'test_type': 'brightness'}},
            {39: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'center', 'test_type': 'caliper'}},
            {40: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'center', 'test_type': 'basis weight'}},
            {41: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'center', 'test_type': 'brightness'}},
            {42: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'outside', 'test_type': 'caliper'}},
            {43: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {44: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'outside', 'test_type': 'brightness'}},
            {45: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'inside', 'test_type': 'caliper'}},
            {46: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {47: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'inside', 'test_type': 'brightness'}},
            {48: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'center', 'test_type': 'caliper'}},
            {49: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'center', 'test_type': 'basis weight'}},
            {50: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'center', 'test_type': 'brightness'}},
            {51: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'outside', 'test_type': 'caliper'}},
            {52: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {53: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'outside', 'test_type': 'brightness'}},
            {54: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'inside', 'test_type': 'caliper'}},
            {55: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {56: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'inside', 'test_type': 'brightness'}},
            {57: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'center', 'test_type': 'caliper'}},
            {58: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'center', 'test_type': 'basis weight'}},
            {59: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'center', 'test_type': 'brightness'}},
            {60: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'outside', 'test_type': 'caliper'}},
            {61: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {62: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'outside', 'test_type': 'brightness'}},
            {63: {'plant': 'PA', 'vendor': 'CorrChoice Coatings', 'received_date': '05/20/07', 'test_average': 0.7,
                  'position': 'inside', 'test_type': 'caliper'}},
            {64: {'plant': 'PA', 'vendor': 'CorrChoice Coatings', 'received_date': '05/20/07', 'test_average': 0.7,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {65: {'plant': 'PA', 'vendor': 'CorrChoice Coatings', 'received_date': '05/20/07', 'test_average': 0.7,
                  'position': 'inside', 'test_type': 'brightness'}},

        ]
        return test_data

    def FetchDashboardPaperTestValues(self):
        test_data = [
            {0: {'plant': 'ms', 'vendor': 'Jay Packaging', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'inside', 'test_type': 'caliper'}},
            {1: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'inside', 'test_type': 'basis weight'}},
            {2: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'inside', 'test_type': 'brightness'}},
            {3: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'center', 'test_type': 'caliper'}},
            {4: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'center', 'test_type': 'basis weight'}},
            {5: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'center', 'test_type': 'brightness'}},
            {6: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'outside', 'test_type': 'caliper'}},
            {7: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'outside', 'test_type': 'basis weight'}},
            {8: {'plant': 'ms', 'vendor': 'Packaging Corp Amer', 'received_date': '05/14/07', 'test_average': 12.2,
                 'position': 'outside', 'test_type': 'brightness'}},
            {9: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                 'position': 'inside', 'test_type': 'caliper'}},
            {10: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {11: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'inside', 'test_type': 'brightness'}},
            {12: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'center', 'test_type': 'caliper'}},
            {13: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'center', 'test_type': 'basis weight'}},
            {14: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'center', 'test_type': 'brightness'}},
            {15: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'outside', 'test_type': 'caliper'}},
            {16: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {17: {'plant': 'ms', 'vendor': 'CorrChoice Coatings', 'received_date': '05/15/07', 'test_average': 12.7,
                  'position': 'outside', 'test_type': 'brightness'}},
            {18: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'inside', 'test_type': 'caliper'}},
            {19: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {20: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'inside', 'test_type': 'brightness'}},
            {21: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'center', 'test_type': 'caliper'}},
            {22: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'center', 'test_type': 'basis weight'}},
            {23: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'center', 'test_type': 'brightness'}},
            {24: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'outside', 'test_type': 'caliper'}},
            {25: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {26: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/14/07', 'test_average': 22.4,
                  'position': 'outside', 'test_type': 'brightness'}},
            {27: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'inside', 'test_type': 'caliper'}},
            {28: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {29: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'inside', 'test_type': 'brightness'}},
            {30: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'center', 'test_type': 'caliper'}},
            {31: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'center', 'test_type': 'basis weight'}},
            {32: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'center', 'test_type': 'brightness'}},
            {33: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'outside', 'test_type': 'caliper'}},
            {34: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {35: {'plant': 'ms', 'vendor': 'Greif-Riverville', 'received_date': '05/16/07', 'test_average': 0.9,
                  'position': 'outside', 'test_type': 'brightness'}},
            {36: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'inside', 'test_type': 'caliper'}},
            {37: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {38: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'inside', 'test_type': 'brightness'}},
            {39: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'center', 'test_type': 'caliper'}},
            {40: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'center', 'test_type': 'basis weight'}},
            {41: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'center', 'test_type': 'brightness'}},
            {42: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'outside', 'test_type': 'caliper'}},
            {43: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {44: {'plant': 'op', 'vendor': 'Greif-Riverville', 'received_date': '05/17/07', 'test_average': 12.8,
                  'position': 'outside', 'test_type': 'brightness'}},
            {45: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'inside', 'test_type': 'caliper'}},
            {46: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {47: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'inside', 'test_type': 'brightness'}},
            {48: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'center', 'test_type': 'caliper'}},
            {49: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'center', 'test_type': 'basis weight'}},
            {50: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'center', 'test_type': 'brightness'}},
            {51: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'outside', 'test_type': 'caliper'}},
            {52: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {53: {'plant': 'PA', 'vendor': 'Packaging Corp Amer', 'received_date': '05/18/07', 'test_average': 22.3,
                  'position': 'outside', 'test_type': 'brightness'}},
            {54: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'inside', 'test_type': 'caliper'}},
            {55: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {56: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'inside', 'test_type': 'brightness'}},
            {57: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'center', 'test_type': 'caliper'}},
            {58: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'center', 'test_type': 'basis weight'}},
            {59: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'center', 'test_type': 'brightness'}},
            {60: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'outside', 'test_type': 'caliper'}},
            {61: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'outside', 'test_type': 'basis weight'}},
            {62: {'plant': 'ms', 'vendor': 'Kruger Packaging', 'received_date': '05/19/07', 'test_average': 12.4,
                  'position': 'outside', 'test_type': 'brightness'}},
            {63: {'plant': 'PA', 'vendor': 'CorrChoice Coatings', 'received_date': '05/20/07', 'test_average': 0.7,
                  'position': 'inside', 'test_type': 'caliper'}},
            {64: {'plant': 'PA', 'vendor': 'CorrChoice Coatings', 'received_date': '05/20/07', 'test_average': 0.7,
                  'position': 'inside', 'test_type': 'basis weight'}},
            {65: {'plant': 'PA', 'vendor': 'CorrChoice Coatings', 'received_date': '05/20/07', 'test_average': 0.7,
                  'position': 'inside', 'test_type': 'brightness'}},

        ]
        # Process data for Plotly
        vendors = []
        positions = []
        test_averages = []
        for item in test_data:
          for key, value in item.items():
            vendors.append(value['vendor'])
            positions.append(value['position'])
            test_averages.append(value['test_average'])
        return vendors, positions, test_averages

    def split_data(self, data, attr):
        list_of_splits = []
        for obj in data:
            for k, v in obj.items():
                if v[attr] not in list_of_splits:
                    list_of_splits.append(v[attr])
        return list_of_splits

    def FetchDashboardRollTestData(self):
      test_data = [
        {"Date": "2024-08-01", "Roll Number": 'a101', "Test Value": 34.5},
        {"Date": "2024-08-01", "Roll Number": 'a102', "Test Value": 35.0},
        {"Date": "2024-08-02", "Roll Number": 'b101', "Test Value": 34.8},
        {"Date": "2024-08-02", "Roll Number": 'b103', "Test Value": 36.0},
        {"Date": "2024-08-03", "Roll Number": 'c104', "Test Value": 34.9},
        {"Date": "2024-08-03", "Roll Number": 'c101', "Test Value": 35.2},
        {"Date": "2024-08-04", "Roll Number": 'd102', "Test Value": 35.1},
        {"Date": "2024-08-04", "Roll Number": 'd103', "Test Value": 36.2},
        {"Date": "2024-08-05", "Roll Number": 'e104', "Test Value": 34.7},
        {"Date": "2024-08-05", "Roll Number": 'e101', "Test Value": 34.6},
        {"Date": "2024-08-01", "Roll Number": 'a101', "Test Value": 4.5},
        {"Date": "2024-08-01", "Roll Number": 'a102', "Test Value": 5.0},
        {"Date": "2024-08-02", "Roll Number": 'b101', "Test Value": 4.8},
        {"Date": "2024-08-02", "Roll Number": 'b103', "Test Value": 6.0},
        {"Date": "2024-08-03", "Roll Number": 'c104', "Test Value": 4.9},
        {"Date": "2024-08-03", "Roll Number": 'c101', "Test Value": 5.2},
        {"Date": "2024-08-04", "Roll Number": 'd102', "Test Value": 5.1},
        {"Date": "2024-08-04", "Roll Number": 'd103', "Test Value": 6.2},
        {"Date": "2024-08-05", "Roll Number": 'e104', "Test Value": 3.7},
        {"Date": "2024-08-05", "Roll Number": 'j101', "Test Value": 4.6},
      ]
      return test_data

    def FetchPaperTestPieChartValues(self):
      data = [['MS', 5394], ['OP', 3067], ['CC', 314], ['SP', 1100], ['MC', 108], ['PA', 0]]
      return data
    def FetchCombinedTestPieChartValues(self):
      data = [['MS', 5394], ['OP', 3067], ['CC', 314], ['SP', 1100], ['MC', 108], ['PA', 0]]
      return data

