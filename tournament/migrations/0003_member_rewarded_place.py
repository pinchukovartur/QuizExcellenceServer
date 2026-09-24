from django.db import migrations, models


class Migration(migrations.Migration):
    """Отметка о полученной награде.

    Ноль у прежних записей: до этой версии сервер о наградах не знал,
    и отметка жила только на устройстве игрока.
    """

    dependencies = [
        ("tournament", "0002_season_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="rewarded_place",
            field=models.IntegerField(default=0),
        ),
    ]
