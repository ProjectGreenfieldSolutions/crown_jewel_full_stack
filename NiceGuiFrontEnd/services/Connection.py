# nicegui framework libraries
from nicegui import app, ui
from local.Logging import Logger

# Necessary for fetching data
import requests
logger = Logger(__file__)


# Custom Exceptions
class InvalidStatusCodeError(Exception):
    pass

class ConnectionTimeoutError(Exception):
    pass

class ConnectionManager:
    def __init__(self):
        logger.info(message=f"Initialized", details=f"ConnectionManager")
        self.port = "8000"
        self.server_name = "django"
        self.protocol = "http"
        self.headers = {
            "Host": "127.0.0.1", "Accept": "application/json",
        }
        # self.timeout = (3,3)
        self.timeout = None
        self.base = f"{self.protocol}://{self.server_name}_container:{self.port}/api"

    def GetConnection(self, endpoint: str, payload: dict = {}):
        logger.info(message=f"Running connection to django", details="GetConnection")
        # Progress Connection Configuration
        url = self.base + endpoint
        logger.info(message=f"url={url}")

        try:
            if not payload:
                # GET
                response = requests.get(url, timeout=self.timeout, headers=self.headers)
            else:
                # POST
                response = requests.post(url, data=payload, timeout=self.timeout, headers=self.headers)

            if response.status_code == 200:
                results = response.json()
            elif response.status_code == 111:
                raise ConnectionTimeoutError(f"Connection timed out/refused, please contact KTC support (111)")
            else:
                raise InvalidStatusCodeError(f"Invalid Status Code, please contact KTC Support ({response.status_code}).")
        except InvalidStatusCodeError as e:
            logger.error(e)
        except ConnectionTimeoutError as e:
            # TODO - This block didn't execute when a connection timeout actually happened
            logger.error(e)
        except Exception as e:
            # TODO - Instead this block executed during a connection timeout
            # TODO - Indicating that response.status_code wasn't 111
            logger.error(e)
        else:
            logger.debug(message=f"results={results}")
            return results

