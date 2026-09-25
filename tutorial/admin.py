from django.contrib import admin
from django.db.models import Case, IntegerField, Value, When
from django.utils.html import format_html

from tutorial.models import STEPS, TutorialStep


@admin.register(TutorialStep)
class TutorialStepAdmin(admin.ModelAdmin):
    """Воронка обучения: сколько игроков дошло до каждого шага.

    Строк ровно столько, сколько шагов. Игроков поимённо не храним:
    отчёту нужно только число, а строка на каждого раздувала базу.

    Проценты считаются здесь же, чтобы воронка читалась прямо в
    списке — иначе ради неё пришлось бы ходить в /tutorial/.
    """

    list_display = ('order', 'step', 'players', 'of_started',
                    'of_previous', 'lost', 'updated_at')
    readonly_fields = ('step', 'players', 'updated_at')

    def get_queryset(self, request):
        # Воронку считаем один раз на отрисовку списка, а не на каждую
        # строку: иначе девять одинаковых запросов к базе
        self._funnel = {row['step']: row for row in TutorialStep.funnel()}

        # Сортируем по месту в воронке, а не по имени шага: по
        # алфавиту «boost» оказался бы перед «classes», и лесенка
        # перестала бы читаться
        order = Case(
            *[When(step=name, then=Value(number))
              for number, name in enumerate(STEPS, 1)],
            default=Value(len(STEPS) + 1),
            output_field=IntegerField(),
        )

        return super().get_queryset(request).order_by(order)

    def _row(self, step):
        return getattr(self, '_funnel', {}).get(step.step, {})

    @admin.display(description='№')
    def order(self, step):
        return self._row(step).get('order', '—')

    @admin.display(description='Дошло')
    def of_started(self, step):
        value = self._row(step).get('of_started')
        return '—' if value is None else '%s%%' % value

    @admin.display(description='От предыдущего')
    def of_previous(self, step):
        value = self._row(step).get('of_previous')
        if value is None:
            return '—'

        # Заметная потеря — красным: именно её и ищут в воронке
        color = '#b00' if value < 80 else '#333'
        return format_html('<b style="color:{}">{}%</b>', color, value)

    @admin.display(description='Потеряли')
    def lost(self, step):
        value = self._row(step).get('lost')
        return '—' if value is None else value

    def has_add_permission(self, request):
        # Строки заводит сама игра при первом прохождении шага
        return False
