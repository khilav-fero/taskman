# apps/tasks/apps.py
from django.apps import AppConfig

class TasksConfig(AppConfig): # <<< Ensure this is TasksConfig
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'     # <<< Ensure this is apps.tasks