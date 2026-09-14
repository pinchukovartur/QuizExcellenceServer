from django.contrib import admin

from tutorial.models import TutorialStep


@admin.register(TutorialStep)
class TutorialStepAdmin(admin.ModelAdmin):
    list_display = ('game_state_id', 'step', 'created_at')
    list_filter = ('step',)
    search_fields = ('game_state_id',)
