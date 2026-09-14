from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Таблица сохранёнок игроков.

    Зависимость взята на prestige.0001_initial, а не на последнюю
    миграцию: цепочка prestige в репозитории неполная — файла 0002 нет,
    он применён только на проде, — и ссылка на неё ломала бы migrate
    локально.
    """

    initial = True

    dependencies = [
        ('prestige', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='States',
            fields=[
                ('game_state_id', models.CharField(max_length=60,
                                                   primary_key=True,
                                                   serialize=False)),
                ('device_id', models.CharField(default='', max_length=60)),
                ('name', models.CharField(max_length=200)),
                ('state_data', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('prestige', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='prestige.prestige')),
            ],
        ),
    ]
