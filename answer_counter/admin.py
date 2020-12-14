from django.contrib import admin

from .models import AnswerCounter


class AnswerCounterAdmin(admin.ModelAdmin):
    def complexity(self, obj):
        sum_all = (obj.first_answer + obj.second_answer + obj.third_answer + obj.four_answer)
        if sum_all == 0:
            return 0
        return round((sum_all - obj.first_answer) / sum_all, 2)

    list_display = ('quest_hash', 'complexity', 'first_answer', 'second_answer', 'third_answer', 'four_answer', 'updated_at')


admin.site.register(AnswerCounter, AnswerCounterAdmin)
