from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    name = 'feedback'
    # Остальные приложения проекта живут на AutoField (миграции
    # писались до Django 3.2) — указываем явно, иначе Django ругается.
    default_auto_field = 'django.db.models.AutoField'
