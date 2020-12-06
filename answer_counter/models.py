from django.db import models


class AnswerCounter(models.Model):
    quest_hash = models.CharField(primary_key=True, max_length=60)
    first_answer = models.IntegerField(default=0)
    second_answer = models.IntegerField(default=0)
    third_answer = models.IntegerField(default=0)
    four_answer = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quest_hash
