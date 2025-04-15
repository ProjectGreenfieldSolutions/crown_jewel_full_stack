from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractUser, User
from local.Logging import Logger

logger = Logger(__file__)


class AccountManager(BaseUserManager):
    def create_user(self, username=None, password=None, email=None, **kwargs):
        """
        Create and return a user with username, email, and password
        """
        logger.debug(message=f"Creating user | params = username={username} email={email}",
                     details=f"AccountManager.create_user")
        if not username:
            logger.debug(message=f"Username field None.")
            raise ValueError('Users must have a valid username.')

        if not password:
            logger.debug(message=f"Password field None.")
            raise ValueError('Password field must be provided.')

        # TODO - do we fetch email from the ERP?
        # if not email:
        #     logger.debug(message=f"Email field None.")
        #     raise ValueError('Users must have a valid email address.')
        # email = self.normalize_email(email)

        user.set_password(password)
        user.save(using=self._db)
        logger.info(message=f"User with username={username} setup up successfully!")
        return user

    # Keeping for legacy purposes.
    def create_superuser(self, username=None, email=None, password=None, name=None, **kwargs):
        """
        Create and return a superuser with username, email, and password
        """
        logger.debug(message=f"Creating Superuser")
        return self.create_user(username=username, email=email, password=password, name=name, superuser=True)


class Account(AbstractUser):
    # General fields
    email = models.EmailField(null=True)
    name = models.CharField(verbose_name='Full Name', max_length=120, blank=True)
    home_plant = models.CharField(max_length=6)
    preferences = models.JSONField(null=True)

    # Management fields
    is_supervisor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # History fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        logger.debug(message=f"Returning username {self.username}")
        return self.username

    def get_full_name(self):
        logger.debug(message=f"Returning full name {self.name}")
        return self.name

    def get_short_name(self):
        if self.name != '':
            logger.debug(message=f"Name found, fetching {self.name.split()[0]}")
            return self.name.split()[0]
        logger.debug(message=f"Name is blank, returning username {self.username}")
        return self.username

    # Ensure to add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='%(class)s_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='%(class)s_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )
