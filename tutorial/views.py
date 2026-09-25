import json

from django.conf import settings
from django.db.models import F
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from tutorial.models import TutorialStep

# Порядок шагов первого сеанса. Первый — сам запуск игры, дальше шаги
# обучения; разница между соседними и есть воронка. Порядок задан
# здесь, а не выводится из данных: шаг, который никто не прошёл, тоже
# должен быть виден в отчёте — именно на нём игроки и отваливаются.
#
# boost и start — два состояния одного экрана подготовки: первое
# видит тот, кто ещё не выбрал бустер, второе — кто выбрал. Игрок
# проходит одно из двух, поэтому «доля от предыдущего» у start
# считается не от boost, а от того же topic, что и у boost.
#
# repeat идёт последним: подсказку про повторение показывают уже
# после пройденной темы.
STEPS = (
    'launch',
    'play',
    'classes',
    'subjects',
    'topic',
    'theory',
    'boost',
    'start',
    'repeat',
)

#: Шаги, которые не продолжают предыдущий, а идут ему в пару.
#: Значение — шаг, от которого считать долю.
BRANCHES = {'start': 'theory'}


@csrf_exempt
def save(request):
    """Отмечает пройденный шаг: POST на /tutorial_step/.

    Считаем игроков, а не храним каждого: отчёту нужно одно число на
    шаг, а строка на пару «игрок и шаг» раздувала базу без предела.

    От двойного счёта защищает клиент — он помнит отправленное и
    второй раз не шлёт. Здесь повторов не отличить: игрока мы больше
    не запоминаем, в этом и смысл.

    Отвечает явным «ok», чтобы клиент понял, можно ли снять шаг из
    очереди: молчаливый 200 неотличим от оборванного соединения.
    """
    secret_key = request.POST.get("secret_key", "")
    if secret_key != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    game_state_id = request.POST.get("game_state_id", "")
    step = request.POST.get("step", "")
    if not game_state_id or step not in STEPS:
        return HttpResponse(json.dumps({"error": "bad request"}),
                            status=400)

    # F-выражение, а не чтение с записью: два запроса подряд иначе
    # прочитали бы одно значение и один из них потерялся
    TutorialStep.objects.get_or_create(step=step)
    TutorialStep.objects.filter(step=step).update(players=F("players") + 1)

    return HttpResponse(json.dumps({"ok": True}))


def funnel(request):
    """Воронка обучения: /tutorial/?secret_key=...

    Показывает, сколько игроков дошло до каждого шага и какая доля
    осталась от предыдущего — так видно, на каком шаге теряем.
    """
    secret_key = request.GET.get("secret_key", "")
    if secret_key != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    counts = dict(TutorialStep.objects.values_list('step', 'players'))

    started = counts.get(STEPS[0], 0)
    rows = []
    previous = None
    for step in STEPS:
        players = counts.get(step, 0)

        # Ветвящийся шаг сравниваем с его развилкой, а не с соседом по
        # списку: иначе доля выходит больше ста процентов и отчёт врёт
        base = counts.get(BRANCHES[step]) if step in BRANCHES else previous

        rows.append({
            "step": step,
            "players": players,
            # Доля от запустивших игру и от предыдущего шага. None, а не
            # 0: без базы процент посчитать нельзя, и ноль бы соврал.
            "of_started": round(players * 100.0 / started, 1) if started else None,
            "of_previous": (round(players * 100.0 / base, 1)
                            if base else None),
        })

        # Ветка не сдвигает основную линию: следующий шаг считается от
        # того же, от чего считалась она
        if step not in BRANCHES:
            previous = players

    return HttpResponse(json.dumps({"steps": rows}, ensure_ascii=False),
                        content_type="application/json")
