from django.conf import settings
from django.core.management.base import BaseCommand
from api.models.Templates import Plant
from api.models.Account import Account
from api.models.Utility import Litho, Customer, Corrugator, Vendor, Flute, Grade, OrderTestCode, TestType, PaperTestReason, PaperTestPosition, PaperTestType, CombinedBoardTestReason, CombinedBoardTestLayer, CombinedBoardTestType

from local.Logging import Logger
logger = Logger(__file__)

class Command(BaseCommand):
    help = "Create initial users for the application"

    def handle(self, *args, **options):
        users = [
            {
                "username": "jacobatktc",
                "name": "jacob storer",
                "home_plant": "ms",
                "email": "jstorer@kennedytech.com",
                "password": "password1",
            },
            {
                "username": "jayatktc",
                "name": "jay sawdon",
                "home_plant": "ms",
                "email": "jsawdon@kennedytech.com",
                "password": "password2",
            },
        ]

        for user_data in users:
            logger.debug(message=f"user_data={user_data}")
            if not Account.objects.filter(username=user_data["username"]).exists():
                try:
                    logger.info(message=f"Attempting to create user: {user_data['username']}")
                    user = Account.objects.create_superuser(
                        username=user_data['username'],
                        email=user_data['email'],
                        password=user_data['password'],
                        name=user_data['name'],
                    )
                    logger.info(message=f"Created user: {user.username}")
                except Exception as e:
                    logger.error(message=f"Error creating user {user_data['username']}: Error message = {e}")
            else:
                logger.info(message=f"User {user_data['username']} already exists")
