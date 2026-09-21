from django.db import migrations, models


class Migration(migrations.Migration):
    """Подтверждённые покупки: токен, игрок, товар.

    Написана вручную — Django на машине разработки нет.
    """

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("token", models.CharField(max_length=512, primary_key=True,
                                           serialize=False)),
                ("game_state_id", models.CharField(max_length=60)),
                ("product_id", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddIndex(
            model_name="purchase",
            index=models.Index(fields=["game_state_id"],
                               name="purchase_pu_game_st_7a3e21_idx"),
        ),
    ]
