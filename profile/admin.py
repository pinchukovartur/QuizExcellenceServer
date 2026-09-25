from django.contrib import admin

from profile.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("game_state_id", "short", "updated_at")
    search_fields = ("game_state_id",)
    ordering = ("-updated_at",)

    @admin.display(description="Карточка")
    def short(self, profile):
        # Показываем начало JSON: целиком он в список не влезает, а по
        # первым полям видно, дошли данные или пусто
        text = profile.data or "—"
        return text[:120]
