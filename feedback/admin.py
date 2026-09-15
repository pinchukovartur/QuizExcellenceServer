from django.contrib import admin

from feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('kind', 'rating', 'text', 'is_done', 'created_at')
    list_filter = ('kind', 'is_done')
    search_fields = ('text', 'game_state_id', 'question_hash')
