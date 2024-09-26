# from django.apps import AppConfig


# class CartConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'cart'

# =============================================================================

# apps.py
from django.apps import AppConfig


class CartConfig(AppConfig):
    name = 'cart'

    def ready(self):
        import cart.signals