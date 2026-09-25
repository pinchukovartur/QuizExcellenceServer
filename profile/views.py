import json
import random

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from profile.models import Profile
from state.models import States

#: Границы кода игрока. Шесть цифр: диктуются голосом без ошибок и
#: помещаются на экран целиком.
#:
#: Код случайный, а не по порядку: соседние номера иначе подбирались
#: бы перебором, и ребёнку сыпались бы заявки от незнакомых людей.
#: Миллион вариантов на тысячу игроков — попасть наугад почти нельзя.
CODE_MIN = 100000
CODE_MAX = 999999

#: Карточка — это несколько чисел и строк. Мегабайт здесь взяться
#: неоткуда, и такой запрос стоит отклонить, а не сохранять.
MAX_DATA = 4000


def _issue_code(profile):
    """Выдаёт игроку код, если его ещё нет.

    Столкновения разбирает база: поле уникально, и повтор просто
    заставляет попробовать другое число. Проверять занятость заранее
    смысла нет — два запроса подряд всё равно успели бы взять одно и
    то же.
    """
    if profile.code:
        return profile.code

    for _ in range(10):
        code = random.randint(CODE_MIN, CODE_MAX)
        try:
            with transaction.atomic():
                profile.code = code
                profile.save(update_fields=["code"])
            return code
        except IntegrityError:
            continue

    # Десять попыток подряд мимо — значит кодов почти не осталось.
    # Лучше отдать ноль, чем крутить цикл дальше: игра покажет, что
    # код пока недоступен.
    return 0


def _forbidden(request):
    key = request.POST.get("secret_key") or request.GET.get("secret_key")
    return key != settings.API_SECRET_KEY


@csrf_exempt
def save(request):
    """Сохраняет карточку игрока: POST на /profile_save/.

    Что внутри data — дело клиента: сервер её не разбирает и не
    проверяет по полям. Так новые строчки в карточке появляются без
    миграций и без правок здесь.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    game_state_id = request.POST.get("game_state_id", "")
    data = request.POST.get("data", "")

    if not game_state_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    if len(data) > MAX_DATA:
        return HttpResponse(json.dumps({"error": "too big"}), status=400)

    # Проверяем, что это вообще JSON: мусор в базе потом не разберёт
    # ни клиент, ни админка
    if data:
        try:
            json.loads(data)
        except ValueError:
            return HttpResponse(json.dumps({"error": "bad json"}), status=400)

    Profile.objects.update_or_create(
        pk=game_state_id,
        defaults={"data": data},
    )

    return HttpResponse(json.dumps({"ok": True}))


def get(request):
    """Отдаёт карточку игрока: GET /profile_get/?id=...

    По одной: карточка открывается тапом по строке рейтинга, и сразу
    все пятнадцать никому не нужны — таблица показывает имя, место и
    престиж, этого ей хватает.

    Профиля может не быть: игрок со старой версией его не присылал.
    Отвечаем пустой карточкой, а не ошибкой — окну есть что показать
    и без неё.
    """
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    game_state_id = request.GET.get("id", "")
    if not game_state_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    profile = Profile.objects.filter(pk=game_state_id).first()
    if profile is None or not profile.data:
        return HttpResponse(json.dumps({"ok": True, "found": False}))

    try:
        data = json.loads(profile.data)
    except ValueError:
        # Битую запись показываем как отсутствующую: разбирать её
        # нечем, а ронять окно из-за одной строки незачем
        return HttpResponse(json.dumps({"ok": True, "found": False}))

    # Даты подставляет сервер, а не клиент: часы на устройстве
    # переводятся, и «играю с 2019 года» нарисовал бы кто угодно.
    # Заодно их не приходится слать в каждой карточке.
    state = States.objects.filter(pk=game_state_id).first()
    if state is not None:
        data["since"] = state.created_at.date().isoformat()
        data["online"] = state.updated_at.date().isoformat()

    return HttpResponse(json.dumps({"ok": True, "found": True, "data": data}))
