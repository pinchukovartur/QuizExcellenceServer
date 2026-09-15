from django.db import migrations, models


class Migration(migrations.Migration):
    """Лайки и дизлайки вопросов.

    Забрана с прода: файл существовал только там, потому что папка
    likes/migrations была в .gitignore.
    """

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('quest_hash', models.CharField(max_length=60,
                                                primary_key=True,
                                                serialize=False)),
                ('likes', models.IntegerField(default=0)),
                ('dislikes', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
