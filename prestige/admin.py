from django.contrib import admin

from .models import Prestige


class PrestigeAdmin(admin.ModelAdmin):
    list_display = ('game_state_id', 'name', 'prestige', 'created_at', 'updated_at')

admin.site.register(Prestige, PrestigeAdmin)