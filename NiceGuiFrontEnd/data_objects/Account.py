from nicegui import ui, app


class AccountData:
  def __init__(self):
    app.logger.info(f"AccountData class has been initialized")
    self.authenticated = False
    self.username = ""
    self.email = ""
    self.first_name = ""
    self.full_name = ""

  @staticmethod
  def MakeConnection(endpoint, payload):
    app.logger.debug(message=f"MakeConnection endpoint={endpoint} | payload={payload}")
    return app.connection_manager.GetConnection(endpoint=endpoint, payload=payload)

  def UserLogin(self, username: str, password: str) -> None:
    app.logger.info(message=f"Attempting to log the user in")
    endpoint = "/accounts/login"
    payload = {"username": username, "password": password}
    results = self.MakeConnection(endpoint=endpoint, payload=payload)
    if results:
      app.logger.info(message=f"Results fetched from UserLogin connection")
      app.logger.debug(message=f"results={results}")
      self.username = results["username"]
      self.full_name = results["full_name"]
      self.first_name = results["first_name"]
      self.email = results["email"]
      ui.notify(f"Username {results['username']} successfully logged in")
    else:
      app.logger.info(message=f"UserLogin failed")
      app.logger.debug(message=f"results={results}")
      ui.notify(results["error"])
