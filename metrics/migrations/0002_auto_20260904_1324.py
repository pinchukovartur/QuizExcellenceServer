from django.db import migrations, models


class Migration(migrations.Migration):
    """Переименование индекса под автоимя Django.

    В 0001 индекс назван вручную, а Django ожидает своё имя с хешем и
    на каждом makemigrations предлагает пересоздать его. Миграция
    закрывает это расхождение раз и навсегда; данных не касается.

    Создана прямо на проде и оттуда же забрана — без неё цепочка
    metrics на других окружениях расходится с боевой.
    """

    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='activityday',
            name='metrics_act_first_d_idx',
        ),
        migrations.AddIndex(
            model_name='activityday',
            index=models.Index(fields=['first_day', 'day'],
                               name='metrics_act_first_d_01ebbf_idx'),
        ),
    ]
