from django.apps import AppConfig


class RendezVousConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rendez_vous'

    def ready(self):
        import rendez_vous.signals
