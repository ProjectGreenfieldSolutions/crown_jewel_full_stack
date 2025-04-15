# core import
from nicegui import app, ui, run
# in house components
from components.widgets.LogoutButton import LogoutButton
from fastapi.responses import RedirectResponse

# Import time specifically for simulated loading
import time
import os
import datetime
from local.globals import AUTO_LOGOUT_ENABLED


class WebApp:
    """
    this is the core app functionality
    pages are created dynamically from a dictionary defined as 'pages_dict' and 'dev_dict'
    dev pages have altered security for access
    this base also creates dynamic navigation, login and out, a header, and a footer for each page
    login is checked before anything is rendered, configuration of it is optional
    a new storage secret must be set on a per app basis
    common methods to over write have included:
    footer
    construct_login_page
    preload
    implementation can be found in the Quality Dash app
    CallBefore and CallAfter methods are defined at the page level, preload is defined at app level
    """
    pages_dict = {}
    dev_dict = {}
    title = ""

    def __init__(self, storage_secret='CHANGEME'):
        # add static files to root directory, for now this includes our logo
        proj_dir = os.path.dirname(__file__)  # Dir of app
        app.add_static_files('/media', os.path.join(proj_dir, 'assets'))
        # setup for client tracking
        # time delta defining users that are inactive, an additional 15 minutes is given before forcing log out
        self.inactive_logout_time = 60 * 15
        # the rate at which 'tick_time' will be fired, this is for custom app level behaviour but also the auto logout
        self.tick_time = 1.0
        # do not alter this, it just houses client data and will be frequently cleared/updated
        self.clients = {}

        # default pages
        self.root_page()
        self.login_page()

        # this can be used in many ways, and does show up in the nav, however
        # it can be omitted if not needed
        # omitted as it is not needed
        # self.profile_page()
        # Dynamically create pages
        for route, page_info in self.pages_dict.items():
            self.create_page(route, page_info)
        # Dynamically create dev pages
        for route, page_info in self.dev_dict.items():
            self.create_restricted_page(route, page_info)
        ui.run(storage_secret=storage_secret)

    def create_page(self, route, page_info):
        """
        creates an unrestricted dynamic page
        """
        @ui.page(f'/{route}')
        async def dynamic_page(page_info=page_info):
            """
            a dynamic method returning a new page on a new route
            this case simply checks if the user is logged in, then constructs the page
            """
            self.user_is_logged_in()
            await self.construct_page(page_info)

    def create_restricted_page(self, route, page_info):
        """
        creates a page with restricted access
        """
        @ui.page(f'/{route}')
        async def dynamic_page(page_info=page_info):
            """
            a dynamic method returning a new page on a new route
            this case checks if the user is logged in, and if the user has super user access,
            then constructs the page
            """
            self.user_is_logged_in()
            self.user_is_dev()
            await self.construct_page(page_info)

    async def construct_page(self, page_info):
            """
            this does the actual construction of the ui
            we first set each route to await a user connection
            on connection we show a splash screen and await preloaded data
            then we run any CallBefore method on the screen class
            from here we instantiate the screen itself with all boilerplate additions
            this includes header, nav and footer.
            finally, we try to call a CallAfter method on the screen class
            """
            await ui.context.client.connected()
            client = ui.context.client
            if not app.storage.user.get('authenticated', False):
                ui.navigate.to('/login')
            else:
                self.clients[client.ip] = {"last_update": datetime.datetime.now()}

            #show splash
            splash = self.show_splash_screen()
            splash.open()
            #await load
            await run.io_bound(self.preload)
            page_class = page_info['page']
            try:
                await run.io_bound(lambda : page_info['page'].CallBefore(self))
            except:
                app.logger.info(f"{page_class} has no CallBefore method implemented, info only")
            #show page
            await self.build_navigation(page_info['title'])
            #Todo: investigate how to make this cpu bound
            page_instance = page_class()  # Instantiate the page class or function
            await self.footer()
            # TODO - Added this a hot fix, but is it needed?
            with page_instance:
                await page_instance.CallAfter()

            #close splash
            splash.close()
            page_instance.on('mousemove', lambda : self.mouse_move(ui.context.client))
            ui.timer(self.tick_time, lambda: self.tick_second(ui.context.client))

    def tick_second(self, client):
        """ called at the defined interval, if this gets used in a subclass please include a call to super """
        if not AUTO_LOGOUT_ENABLED:
            return

        if self.clients != {}:
            if datetime.datetime.now() - self.clients[client.ip]['last_update'] > datetime.timedelta(seconds=self.inactive_logout_time):
                ui.notify("Still there? You will automatically be logged out in 10 seconds if activity is not detected.")
            if datetime.datetime.now() - self.clients[client.ip]['last_update'] > datetime.timedelta(seconds=self.inactive_logout_time + 10):
                ui.notify("Logging out due to inactivity.")
                app.storage.user.clear()
                ui.open('/login')
        else:
            ui.notify("Logging out due to inactivity.")
            app.storage.user.clear()
            ui.open('/login')

    def mouse_move(self, client):
        """
        called when client side mouse movement is detected
        if this gets used in a subclass please include a call to super
        """
        if self.clients != {} and self.clients.keys().__contains__(client.ip):
           self.clients[client.ip]['last_update'] = datetime.datetime.now()
        else:
            self.clients[client.ip] = {"last_update": datetime.datetime.now()}

    def login_page(self):
        """
        dynamically return the login route as needed
        """
        @ui.page(f'/login')
        async def dynamic_page():
            """
            dynamically construct the login page
            """
            await self.construct_login_page()  # Instantiate the page class or function

    def profile_page(self):
        """
        dynamically return the login route as needed
        """
        pass

    def root_page(self):
        """
        dynamically return the root route
        """
        @ui.page(f'/')
        async def dynamic_page():
            """
            dynamically construct the dashboard page
            this should get over written if not using a dashboard page
            """
            self.user_is_logged_in()
            return RedirectResponse("/dashboard")

    # define auth functions here to keep main clean
    def user_is_logged_in(self):
        """
        authenticate the user, this method will return users to the login screen
        if user storage doesn't contain a 'true' value for 'authenticated'
        if it does, this method does nothing and is ignored
        """
        if not app.storage.user.get('authenticated', False):
            app.logger.warning('user not auth')
            return RedirectResponse("/login")

    def user_is_dev(self):
        """
        Similar to the method above, this method checks if the user is logged in,
        then checks the the user type is either 'dev' or 'super'
        in the case that it is not, this will return the user to dashboard,
        this prevents users from direct accessing pages they don't have navigation access to
        via direct url
        """
        self.user_is_logged_in()
        if app.storage.user['type'] not in ['admin', 'supervisor']:
            return RedirectResponse("/dashboard")

    async def construct_login_page(self):
        """
        this method simply constructs the login page
        """
        with ui.card().classes('absolute-center w-full h-full'):
            with ui.column().classes('absolute-center h-full'):
                self.username = ui.input('Username').on('keydown.enter', self.try_login).classes('center')
                self.password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter',
                                                                                                    self.try_login).classes(
                    'center')
                ui.button('Log in', on_click=self.try_login).classes('center w-full')

    def try_login(self):
        """
        Check the input password against the user entry from the array.
        TODO: USE DATABASE AUTH
        """
        user_data = USERS.get(self.username.value)
        if not user_data or self.password.value != user_data['pass']:
            ui.notify('Incorrect Username or Password')
            return

        # Redirect to home page
        return RedirectResponse("/")

    async def build_navigation(self, current_page="Lorem ipsum"):
        """
        dynamically build a navigation panel for each page
        self.title is the title displayed throughout the application
        and current page is the display version of the route, set in the screen dict
        """
        ui.page_title(f"{self.title} - {current_page}")
        with ui.header(elevated=True).style('background-color: #349716'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.button(on_click=lambda: ui.open("/"), icon='home').props('flat color=white')
            ui.label(f'{self.title} - {current_page}').style('font-size: 200%; font-weight: 300')
        with ui.left_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered') as left_drawer:
            left_drawer.hide()
            ui.label("Navigation")
            ui.separator()
            for route, page_info in self.pages_dict.items():
                ui.button(f"{page_info['title']}", on_click=lambda r=route: ui.open(f'/{r}')).classes('w-full')
            if app.storage.user.get('type') in ['dev', 'super']:
                ui.label("Super User Pages")
                ui.separator()
                for route, page_info in self.dev_dict.items():
                    ui.button(f"{page_info['title']}", on_click=lambda r=route: ui.open(f'/{r}')).classes(
                        'w-full')

            ui.separator()
            LogoutButton()


    async def footer(self):
        """ dynamically return a boilerplate footer for use on every screen """
        with ui.footer().style('background-color: #349716') as foot:
            ui.label(f'{self.title}')

    def show_splash_screen(self):
        """ construct a dialog for use as an app wide splash screen """
        with ui.dialog().props('maximized') as dialog, ui.card().style('justify-content: center;'):
            img = ui.image("/media/img.png")
            with img:
                ui.spinner(size="large", color='white')
            with ui.row().classes("h-1/8 w-full justify-center"):
                ui.label("Loading Data").classes("h-1/8 justify-center")
        return dialog

    def preload(self):
        """ over write this in child class to preload data before displaying screen """
        time.sleep(1)
