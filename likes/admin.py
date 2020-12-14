from django.contrib import admin

from likes.models import Likes


class LikesAdmin(admin.ModelAdmin):
    def percent_dislikes(self, obj):
        if obj.likes == 0 or obj.dislikes == 0:
            return 0
        return round(obj.dislikes / (obj.dislikes + obj.likes), 2)

    list_display = ('quest_hash', 'likes', 'dislikes', 'updated_at', 'percent_dislikes')


admin.site.register(Likes, LikesAdmin)
