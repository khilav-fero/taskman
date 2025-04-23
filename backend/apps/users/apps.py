# apps/users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig): # <<< CORRECT CLASS NAME
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'     # <<< CORRECT APP PATH NAME