from django.db import models


class Likes(models.Model):
    quest_hash = models.CharField(primary_key=True, max_length=60)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quest_hash
