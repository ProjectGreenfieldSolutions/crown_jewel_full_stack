copy the contents of this directory to root.local before getting started
this directory contains boiler-plate logging and asana automation
you also need nicegui, requests, an asana access token and an asana project for the asana automation
the asana project id can be found from the project url:
from https://app.asana.com/0/1111111111/2222222222
the project id is 1111111111 access token can be created in the asana dev portal

I tried to add this to .git/pre-commit but saw issues making this useful to other developers, the workaround for now is to run this script as needed

logger is instantiated app wide by default, if this was done correctly it can be accessed through app.logging and used with app.logging.info/warning()
