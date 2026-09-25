import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from state.models import States
from prestige.models import Prestige


def _get_current_state(state_id, name):
    try:
        prestige = Prestige.objects.get(game_state_id=state_id)
    except ObjectDoesNotExist:
        prestige = Prestige.objects.create(game_state_id=state_id, name=name, prestige=0)

    try:
        state = States.objects.get(pk=state_id)
    except ObjectDoesNotExist:
        state = States.objects.create(game_state_id=state_id, prestige=prestige, name=name)
    return state


@csrf_exempt
def update(request):
    secret_key = request.POST["secret_key"]
    user_id = request.POST["user_id"]
    device_id = request.POST["device_id"]
    new_name = request.POST["new_name"]
    new_prestige = request.POST["new_prestige"]
    new_state = request.POST["new_state"]
    # Через get, а не по ключу: клиенты старых версий платформу не
    # шлют, и обязательный параметр обрушил бы им сохранение
    platform = request.POST.get("platform", "")

    if secret_key != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    state = _get_current_state(user_id, new_name)

    prestige = state.prestige
    prestige.prestige = new_prestige
    prestige.save()

    state.name = new_name
    state.device_id = device_id
    state.state_data = new_state
    # Пустое значение не записываем: игрок со старой версией иначе
    # стирал бы платформу, узнанную при прошлом сохранении
    if platform:
        state.platform = platform
    state.save()

    return HttpResponse(json.dumps({"ok": "complete save"}))


@csrf_exempt
def delete(request):
    """Убирает сохранёнку удалённого профиля.

    Без этого профиль возвращался бы при следующем запуске: на сервере
    у него остаётся прежний престиж, и get_best_state сочтёт его лучше
    чистого локального.
    """
    secret_key = request.POST["secret_key"]
    user_id = request.POST["user_id"]
    device_id = request.POST["device_id"]

    if secret_key != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    # Сверяем устройство: чужую сохранёнку по одному лишь id удалять нельзя
    removed, _ = States.objects.filter(pk=user_id, device_id=device_id).delete()

    return HttpResponse(json.dumps({"ok": "deleted", "count": removed}))


def find(request):
    """Ищет сохранёнки по нику: /state_find/?secret_key=...&name=...

    Нужна поддержке: игрок пишет в отзыв ник, а device_id и
    game_state_id знает только его устройство. Без этого найти
    человека, который просит помощи, нечем.

    Отдаёт метаданные, но не сам state_data: он большой, а для
    опознания хватает престижа и дат.
    """
    if request.GET.get("secret_key") != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    name = request.GET.get("name", "").strip()
    if not name:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    rows = States.objects.filter(name__icontains=name)[:20]

    return HttpResponse(json.dumps({
        "items": [{
            "game_state_id": r.game_state_id,
            "device_id": r.device_id,
            "name": r.name,
            "prestige": r.prestige.prestige,
            "state_size": len(r.state_data or ""),
            "created_at": r.created_at.isoformat(),
            "updated_at": r.updated_at.isoformat(),
        } for r in rows],
    }, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def get_best_state(request):
    secret_key = request.POST["secret_key"]
    device_id = request.POST["device_id"]
    prestige = request.POST["prestige"]

    int_prestige = int(prestige)

    if secret_key != settings.API_SECRET_KEY:
        return HttpResponseForbidden("forbidden")

    state = States.objects.filter(device_id=device_id).first()
    if state and int_prestige <= state.prestige.prestige:
        return HttpResponse(json.dumps({"is_find": "true", "state": state.state_data}))

    return HttpResponse(json.dumps({"result": "Not found best state!"}))

