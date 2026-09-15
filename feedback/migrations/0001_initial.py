from django.db import migrations, models


class Migration(migrations.Migration):
    """Таблица сообщений от игроков.

    Зависимостей нет намеренно, как у metrics и tutorial: feedback не
    ссылается на prestige внешним ключом, только строковым
    game_state_id. Цепочка миграций prestige в репозитории неполная
    (файла 0002 нет, он применён только на проде).
    """

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('game_state_id', models.CharField(db_index=True, max_length=60)),
                ('kind', models.CharField(
                    choices=[('error', 'Ошибка в вопросе'),
                             ('rate', 'Оценка игры')],
                    db_index=True, max_length=16)),
                ('text', models.TextField()),
                ('question_hash', models.CharField(blank=True, default='',
                                                   max_length=64)),
                ('subject_id', models.CharField(blank=True, default='',
                                                max_length=40)),
                ('rating', models.IntegerField(default=0)),
                ('version', models.CharField(blank=True, default='',
                                             max_length=20)),
                ('is_done', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True,
                                                    db_index=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='feedback',
            index=models.Index(fields=['is_done', 'created_at'],
                               name='feedback_fe_done_idx'),
        ),
    ]
