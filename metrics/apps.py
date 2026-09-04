from django.apps import AppConfig


class MetricsConfig(AppConfig):
    name = 'metrics'
    # Остальные приложения проекта живут на AutoField (миграции
    # писались до Django 3.2), и миграция metrics создана такой же —
    # указываем явно, иначе Django ругается на несовпадение.
    default_auto_field = 'django.db.models.AutoField'
