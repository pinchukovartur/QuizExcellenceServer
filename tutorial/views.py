import json

from django.conf import settings
from django.db.models import F
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from tutorial.models import STEPS, TutorialStep




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

    rows = TutorialStep.funnel()

    return HttpResponse(json.dumps({"steps": rows}, ensure_ascii=False),
                        content_type="application/json")
