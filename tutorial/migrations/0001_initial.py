from django.db import migrations, models


class Migration(migrations.Migration):
    """Таблица пройденных шагов обучения.

    Зависимостей нет намеренно: tutorial не ссылается на prestige
    внешним ключом, только строковым game_state_id. Цепочка миграций
    prestige в репозитории неполная (файла 0002 нет, он применён
    только на проде), и зависимость от неё ломала бы migrate локально.
    """

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TutorialStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('game_state_id', models.CharField(db_index=True, max_length=60)),
                ('step', models.CharField(db_index=True, max_length=40)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='tutorialstep',
            index=models.Index(fields=['step', 'created_at'],
                               name='tutorial_tu_step_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='tutorialstep',
            unique_together={('game_state_id', 'step')},
        ),
    ]
