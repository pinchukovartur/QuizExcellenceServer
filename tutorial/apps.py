from django.apps import AppConfig


class TutorialConfig(AppConfig):
    name = 'tutorial'
    # Остальные приложения проекта живут на AutoField (миграции
    # писались до Django 3.2) — указываем явно, иначе Django ругается
    # на несовпадение.
    default_auto_field = 'django.db.models.AutoField'
