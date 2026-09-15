from django.db import migrations, models


class Migration(migrations.Migration):
    """Иконка игрока для лидерборда.

    Зависимость указана на 0002_auto_20181027_2354: файла этой миграции
    в репозитории нет, но в базе она числится применённой (именно она
    сделала game_state_id первичным ключом). Поэтому нумеруемся с 0003.
    """

    dependencies = [
        ('prestige', '0002_auto_20181027_2354'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestige',
            name='avatar',
            field=models.IntegerField(default=-1),
        ),
    ]
