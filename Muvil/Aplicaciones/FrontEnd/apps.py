from django.apps import AppConfig


class FrontendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Aplicaciones.FrontEnd'

# APScheduler
    def ready(self):
        from . import updater
        updater.start()
