from django.db import migrations, models


class Migration(migrations.Migration):
    """Профиль перестаёт быть привязан к стейту.

    Код друга и список нужны с первого запуска, а сохранёнка на
    сервере появляется только после пройденной темы: игрок открывал
    вкладку друзей и видел прочерк вместо своего кода.

    Заводить ради профиля пустой стейт нельзя — вместе с ним пришлось
    бы создавать и пустой Prestige, а он портит метрику конверсии.
    Поэтому game_state_id становится обычным ключом, а осиротевшие
    профили подчищает удаление игрока (state.views.delete).

    Таблицу пересоздаём: в SQLite первичный ключ иначе не сменить, а
    данных в ней пока нет — только коды, выданные при проверках.
    """

    dependencies = [
        ("profile", "0003_friendship"),
    ]

    operations = [
        # Индекс и уникальность ссылаются на поля, которые сейчас
        # уходят: снимаем их первыми, иначе таблицу не пересобрать
        migrations.AlterUniqueTogether(name="friendship", unique_together=set()),
        migrations.RemoveIndex(
            model_name="friendship",
            name="profile_fri_owner_i_bf1391_idx",
        ),
        migrations.RemoveField(model_name="friendship", name="friend"),
        migrations.RemoveField(model_name="friendship", name="owner"),
        migrations.DeleteModel(name="Profile"),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("game_state_id", models.CharField(
                    max_length=60, primary_key=True, serialize=False)),
                ("data", models.TextField(blank=True, default="")),
                ("code", models.IntegerField(
                    blank=True, db_index=True, null=True, unique=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="friendship",
            name="owner",
            field=models.ForeignKey(
                on_delete=models.CASCADE, related_name="friends",
                to="profile.profile"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="friendship",
            name="friend",
            field=models.ForeignKey(
                on_delete=models.CASCADE, related_name="friend_of",
                to="profile.profile"),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="friendship", unique_together={("owner", "friend")}),
        migrations.AddIndex(
            model_name="friendship",
            index=models.Index(
                fields=["owner", "created_at"],
                name="profile_fri_owner_i_bf1391_idx"),
        ),
    ]
