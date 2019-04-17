from django.contrib import admin

from .models import QuizWordPrestige


class PrestigeAdmin(admin.ModelAdmin):
    list_display = ('game_state_id', 'name', 'prestige', 'created_at', 'updated_at')


admin.site.register(QuizWordPrestige, PrestigeAdmin)
