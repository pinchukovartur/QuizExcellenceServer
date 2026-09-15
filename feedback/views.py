import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from feedback.models import Feedback

# Длиннее не нужно: это жалоба игрока, а не переписка. Лишнее режем,
# чтобы одно сообщение не заняло базу целиком.
MAX_TEXT = 2000

# Сколько сообщений отдаём за раз — скрипт мониторинга ходит регулярно
PAGE = 200


def _forbidden(request):
    """Секрет обязателен: без него удалять и читать чужие жалобы
    мог бы кто угодно."""
    key = request.POST.get("secret_key") or request.GET.get("secret_key", "")
    return key != settings.API_SECRET_KEY


@csrf_exempt
def add(request):
    """Принимает сообщение игрока: POST на /feedback_add/."""
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    text = request.POST.get("text", "").strip()
    kind = request.POST.get("kind", Feedback.KIND_ERROR)
    game_state_id = request.POST.get("game_state_id", "")

    if not text or kind not in dict(Feedback.KINDS):
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    try:
        rating = int(request.POST.get("rating", "0"))
    except ValueError:
        rating = 0

    item = Feedback.objects.create(
        game_state_id=game_state_id,
        kind=kind,
        text=text[:MAX_TEXT],
        question_hash=request.POST.get("question_hash", "")[:64],
        subject_id=request.POST.get("subject_id", "")[:40],
        rating=rating,
        version=request.POST.get("version", "")[:20],
    )

    # Отвечаем id: по нему сообщение потом удаляют
    return HttpResponse(json.dumps({"ok": True, "id": item.id}))


@csrf_exempt
def delete(request):
    """Удаляет сообщение: POST на /feedback_delete/ с id.

    Нужно, когда жалоба разобрана и держать её незачем — например,
    это был спам. Для «разобрано, но пусть останется» есть done.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    item_id = request.POST.get("id", "")
    if not item_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    removed, _ = Feedback.objects.filter(pk=item_id).delete()

    return HttpResponse(json.dumps({"ok": True, "deleted": removed}))


@csrf_exempt
def done(request):
    """Помечает сообщение разобранным, не удаляя: POST на /feedback_done/.

    По разобранным видно историю правок — что уже чинили и когда.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    item_id = request.POST.get("id", "")
    if not item_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    updated = Feedback.objects.filter(pk=item_id).update(is_done=True)

    return HttpResponse(json.dumps({"ok": True, "updated": updated}))


def items(request):
    """Список сообщений: /feedback/?secret_key=...

    По умолчанию отдаёт неразобранные — именно их смотрит скрипт
    мониторинга. `all=1` показывает и закрытые, `kind` фильтрует поток.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    rows = Feedback.objects.all()
    if request.GET.get("all") != "1":
        rows = rows.filter(is_done=False)

    kind = request.GET.get("kind")
    if kind in dict(Feedback.KINDS):
        rows = rows.filter(kind=kind)

    rows = rows.order_by('-created_at')[:PAGE]

    return HttpResponse(json.dumps({
        "items": [{
            "id": r.id,
            "kind": r.kind,
            "text": r.text,
            "rating": r.rating,
            "question_hash": r.question_hash,
            "subject_id": r.subject_id,
            "version": r.version,
            "game_state_id": r.game_state_id,
            "created_at": r.created_at.isoformat(),
        } for r in rows],
    }, ensure_ascii=False), content_type="application/json")
