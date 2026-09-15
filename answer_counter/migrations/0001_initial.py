from django.db import migrations, models


class Migration(migrations.Migration):
    """Счётчик ответов по вариантам — из него берутся проценты в игре.

    Забрана с прода: файл существовал только там, потому что папка
    answer_counter/migrations была в .gitignore.
    """

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerCounter',
            fields=[
                ('quest_hash', models.CharField(max_length=60,
                                                primary_key=True,
                                                serialize=False)),
                ('first_answer', models.IntegerField(default=0)),
                ('second_answer', models.IntegerField(default=0)),
                ('third_answer', models.IntegerField(default=0)),
                ('four_answer', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
