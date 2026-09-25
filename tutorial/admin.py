from django.contrib import admin

from tutorial.models import TutorialStep


@admin.register(TutorialStep)
class TutorialStepAdmin(admin.ModelAdmin):
    """Воронка обучения: сколько игроков дошло до каждого шага.

    Строк ровно столько, сколько шагов. Игроков поимённо не храним:
    отчёту нужно только число, а строка на каждого раздувала базу.
    """

    list_display = ('step', 'players', 'updated_at')
    ordering = ('-players',)
    readonly_fields = ('updated_at',)
