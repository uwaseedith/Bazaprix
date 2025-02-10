from django.apps import AppConfig


class BazaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Baza'

    def ready(self):
        import Baza.signals