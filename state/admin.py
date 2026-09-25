from django.contrib import admin

from state.models import States


class StateAdmin(admin.ModelAdmin):

    list_display = ('game_state_id', 'platform', 'device_id', 'name',
                    'created_at', 'updated_at')
    # Фильтр по магазину: сервер общий, и аудиторию AppGallery иначе
    # из списка не выделить
    list_filter = ('platform',)
    search_fields = ('game_state_id', 'device_id', 'name')


admin.site.register(States, StateAdmin)
