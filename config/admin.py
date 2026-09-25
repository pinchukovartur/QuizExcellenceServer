from django.contrib import admin

from config.models import Setting


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    """Настройки игры.

    Строки заводит код при первом чтении — руками их создавать не
    нужно, и незнакомый ключ ни на что не повлияет.
    """

    list_display = ("key", "value", "note", "updated_at")
    list_editable = ("value",)
    search_fields = ("key", "note")
    readonly_fields = ("key", "note", "updated_at")

    def has_add_permission(self, request):
        # Добавлять руками нечего: ключи заводит код, а чужой никто
        # не прочитает
        return False
