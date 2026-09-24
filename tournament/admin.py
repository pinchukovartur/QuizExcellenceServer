from django.contrib import admin
from django.utils import timezone

from tournament.models import Member, Room, Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """Запуски турнира: здесь задаются даты начала и конца.

    Сервер сам сезоны не создаёт — что заведено здесь, то и идёт.
    Между запусками турнира нет, и это нормально: событие, которое
    идёт всегда, перестаёт быть событием.
    """

    list_display = ("title", "started_at", "finished_at", "state",
                    "rooms_count", "players_count")
    list_filter = ("started_at",)
    ordering = ("-started_at",)

    @admin.display(description="Состояние")
    def state(self, season):
        now = timezone.now()
        if season.started_at > now:
            days = (season.started_at - now).days
            return f"начнётся через {days} дн."
        if season.finished_at <= now:
            return "завершён"

        days = (season.finished_at - now).days
        return f"идёт, осталось {days} дн."

    @admin.display(description="Комнат")
    def rooms_count(self, season):
        return season.rooms.count()

    @admin.display(description="Игроков")
    def players_count(self, season):
        return Member.objects.filter(room__season=season).count()


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "season", "players_count", "created_at")
    list_filter = ("season",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "score", "reward", "room", "updated_at")
    list_filter = ("room__season", "rewarded_place")
    search_fields = ("name", "game_state_id")
    ordering = ("-score",)

    @admin.display(description="Награда")
    def reward(self, member):
        if not member.rewarded_place:
            return "—"

        return f"забрал за {member.rewarded_place} место"
