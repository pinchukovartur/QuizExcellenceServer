from django.db import migrations, models


class Migration(migrations.Migration):
    """Таблица дней активности.

    Зависимостей нет намеренно: metrics не ссылается на prestige
    внешним ключом, только строковым game_state_id. Цепочка миграций
    prestige в репозитории неполная (файла 0002 нет, он применён
    только на проде), и зависимость от неё ломала бы migrate локально.
    """

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('game_state_id', models.CharField(db_index=True, max_length=60)),
                ('day', models.DateField(db_index=True)),
                ('prestige', models.IntegerField(default=0)),
                ('first_day', models.DateField(db_index=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='activityday',
            unique_together={('game_state_id', 'day')},
        ),
        migrations.AddIndex(
            model_name='activityday',
            index=models.Index(fields=['first_day', 'day'],
                               name='metrics_act_first_d_idx'),
        ),
    ]
