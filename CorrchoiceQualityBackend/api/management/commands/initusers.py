from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from api.models.Account import Account

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
            {
                "username": "ben",
                "name": "ben donley",
                "home_plant": "ms",
                "email": "bdonley@kennedytech.com",
                "password": "ben",
            },
            {
                "username": "mccarron",
                "name": "mccarron",
                "home_plant": "ms",
                "email": "jmccarron@kennedytech.com",
                "password": "mccarron",
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
