from django.contrib import admin

from likes.models import Likes


class LikesAdmin(admin.ModelAdmin):
    list_display = ('quest_hash', 'likes', 'dislikes', 'updated_at')


admin.site.register(Likes, LikesAdmin)
