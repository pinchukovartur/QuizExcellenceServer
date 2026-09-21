from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    """Турниры: сезон, комнаты по 15 игроков и их очки.

    Написана вручную: Django на машине разработки не установлен, а
    makemigrations без него не запустить. Структура повторяет
    tournament/models.py — при расхождении Django пожалуется на
    незаписанные изменения.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Season",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(
                    default=django.utils.timezone.now)),
                ("finished_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name="ID")),
                ("players_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("season", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="rooms", to="tournament.season")),
            ],
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name="ID")),
                ("game_state_id", models.CharField(max_length=60)),
                ("name", models.CharField(default="", max_length=200)),
                ("avatar", models.IntegerField(default=-1)),
                ("score", models.IntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("room", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="members", to="tournament.room")),
            ],
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["game_state_id"],
                               name="tournament__game_st_d65f14_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="member",
            unique_together={("room", "game_state_id")},
        ),
    ]
