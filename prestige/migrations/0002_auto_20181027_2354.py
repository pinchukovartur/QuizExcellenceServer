from django.db import migrations, models


class Migration(migrations.Migration):
    """Восстановленная миграция: game_state_id становится первичным ключом.

    Файла не было в репозитории — на продакшене она применена с 2018
    года, а в чистой копии migrate падал с NodeNotFoundError, потому что
    0003 на неё ссылается. Обнаружилось при локальной проверке на
    поднятом Django.

    Содержимое восстановлено по 0001_initial и нынешней модели: id
    убран, game_state_id стал ключом и подрос до 60 символов. Имя файла
    оставлено прежним, чтобы на сервере миграция считалась уже
    применённой и база не тронулась.
    """

    dependencies = [
        ('prestige', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prestige',
            name='id',
        ),
        migrations.AlterField(
            model_name='prestige',
            name='game_state_id',
            field=models.CharField(max_length=60, primary_key=True,
                                   serialize=False),
        ),
    ]
