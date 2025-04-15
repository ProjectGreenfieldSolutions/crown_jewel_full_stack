# nicegui framework libraries
from nicegui import app, ui

# Necessary for fetching data
import requests

def FetchApiData(django_appendix):
    # Leaving just in case
    # # Fetch first URL of application listed urls
    # url = next(iter(app.urls))

    base = "http://django_container:8000"
    url = base + django_appendix

    try:
        # Host = where packet is coming from
        # Accept = we're accept this kind of data
        headers = {"Host": "127.0.0.1", "Accept": "application/json"}
        response = requests.get(url, timeout=(3, 3), headers=headers)
        if response.status_code == 200:
            results = response.json()
        else:
            raise Exception
    except Exception as e:
        ui.notify("Django API connection failed {e}")
    else:
        results["url"] = url
        ui.timer(5.0, lambda: ui.notify(results))

def TestAllCRUD():
    FetchApiData("/api/create")
    FetchApiData("/api/read")
    FetchApiData("/api/update")
    FetchApiData("/api/delete")

def TestAllCRUDButton():
    ui.button("Test the Django connection", on_click=lambda: TestAllCRUD())