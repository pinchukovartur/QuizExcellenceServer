from django.contrib import admin

from state.models import States


class StateAdmin(admin.ModelAdmin):

    list_display = ('game_state_id', 'device_id', 'name', 'created_at', 'updated_at')


admin.site.register(States, StateAdmin)
