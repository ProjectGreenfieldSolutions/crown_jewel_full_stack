from nicegui import ui, app


class LogoutButton:
  def __init__(self):
    ui.button('Log out', on_click=self.logout).classes('center w-full').props("color='red'")

  def logout(self):
    # Clear user session data
    app.storage.user.clear()
    # Redirect to the login page
    ui.open('/login')