from django.db import migrations, models


def days_to_minutes(apps, schema_editor):
    """Переносит уже заданные окна: было в днях, стало в минутах."""
    Season = apps.get_model("tournament", "Season")
    for season in Season.objects.exclude(closed_before_end_days=None):
        Season.objects.filter(pk=season.pk).update(
            closed_before_end_minutes=season.closed_before_end_days * 24 * 60)


def minutes_to_days(apps, schema_editor):
    """Обратный перенос: минуты округляем до дней вниз."""
    Season = apps.get_model("tournament", "Season")
    for season in Season.objects.exclude(closed_before_end_minutes=None):
        Season.objects.filter(pk=season.pk).update(
            closed_before_end_days=season.closed_before_end_minutes // (24 * 60))


class Migration(migrations.Migration):
    """Окно регистрации переезжает с дней на минуты.

    Сутки — слишком грубый шаг: так нельзя закрыть вход за половину
    дня или за два часа перед концом короткого запуска.

    Значения уже заведённых запусков переносим, а не теряем.
    """

    dependencies = [
        ("tournament", "0004_season_closed_before_end_days"),
    ]

    operations = [
        migrations.AddField(
            model_name="season",
            name="closed_before_end_minutes",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RunPython(days_to_minutes, minutes_to_days),
        migrations.RemoveField(
            model_name="season",
            name="closed_before_end_days",
        ),
    ]
