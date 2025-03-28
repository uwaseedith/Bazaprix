from django.apps import AppConfig
import logging
logging.basicConfig(level=logging.INFO)
logging.info("settings.py/app.py loaded successfully!")

class BazaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Baza'

    def ready(self):
        import Baza.signals