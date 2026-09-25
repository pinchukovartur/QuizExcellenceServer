import django.utils.timezone
from django.db import migrations, models

#: Счётчики, посчитанные до смены схемы. Переживают только время
#: миграции — этого достаточно, обе операции идут подряд.
_counts = {}


def remember_counts(apps, schema_editor):
    """Считает игроков по шагам, пока таблица ещё старая."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT step, COUNT(DISTINCT game_state_id) "
            "FROM tutorial_tutorialstep GROUP BY step")
        _counts.clear()
        _counts.update(dict(cursor.fetchall()))

    # Строки больше не нужны: новая таблица хранит одно число на шаг,
    # а старые записи мешали бы смене первичного ключа
    schema_editor.execute("DELETE FROM tutorial_tutorialstep")


def restore_counts(apps, schema_editor):
    """Кладёт посчитанное в новую таблицу."""
    TutorialStep = apps.get_model("tutorial", "TutorialStep")
    for step, players in _counts.items():
        TutorialStep.objects.create(step=step, players=players)


class Migration(migrations.Migration):
    """Статистика обучения переезжает на счётчики.

    Было по строке на пару «игрок и шаг»: девять записей на человека и
    рост без предела — к паре тысяч игроков это больше десяти тысяч
    строк. Отчёту же нужно одно число на шаг.

    Накопленные цифры переносим: воронка не обнуляется.
    """

    dependencies = [
        ("tutorial", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(remember_counts, migrations.RunPython.noop),
        migrations.RemoveIndex(
            model_name="tutorialstep",
            name="tutorial_tu_step_idx",
        ),
        migrations.AlterUniqueTogether(
            name="tutorialstep",
            unique_together=set(),
        ),
        migrations.RemoveField(model_name="tutorialstep", name="game_state_id"),
        migrations.RemoveField(model_name="tutorialstep", name="created_at"),
        migrations.RemoveField(model_name="tutorialstep", name="id"),
        migrations.AlterField(
            model_name="tutorialstep",
            name="step",
            field=models.CharField(max_length=40, primary_key=True,
                                   serialize=False),
        ),
        migrations.AddField(
            model_name="tutorialstep",
            name="players",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="tutorialstep",
            name="updated_at",
            # auto_now проставит время сам, строк к этому моменту нет
            field=models.DateTimeField(auto_now=True,
                                       default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.RunPython(restore_counts, migrations.RunPython.noop),
    ]
