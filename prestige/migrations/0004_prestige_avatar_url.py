from django.db import migrations, models


class Migration(migrations.Migration):
    """Ссылка на аватарку из аккаунта игровых сервисов.

    Пустая строка у всех прежних записей: игрок не входил в аккаунт,
    и клиент рисует ему иконку из набора приложения.
    """

    dependencies = [
        ('prestige', '0003_prestige_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestige',
            name='avatar_url',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
