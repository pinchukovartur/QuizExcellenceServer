from django.db import migrations, models


class Migration(migrations.Migration):
    """Название запуска для админки.

    Пустое у прежних сезонов: они создавались сервером автоматически и
    имени не имели. В списке такой показывается как «запуск N».
    """

    dependencies = [
        ("tournament", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="season",
            name="title",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterModelOptions(
            name="season",
            options={"ordering": ["-started_at"]},
        ),
    ]
