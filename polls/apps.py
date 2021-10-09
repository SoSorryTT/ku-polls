"""App for poll."""
from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Class for config the poll."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
