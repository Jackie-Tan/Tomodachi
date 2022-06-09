from django.apps import AppConfig


class TomodachiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tomodachi'

    def ready(self):
        from . import signals