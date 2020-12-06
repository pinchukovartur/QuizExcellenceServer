from django.contrib import admin

from .models import AnswerCounter


class AnswerCounterAdmin(admin.ModelAdmin):
    list_display = ('quest_hash', 'first_answer', 'second_answer', 'third_answer', 'four_answer', 'updated_at')


admin.site.register(AnswerCounter, AnswerCounterAdmin)
