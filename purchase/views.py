import json

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from purchase.models import Purchase

# Пакет приложения — в нём заведены товары
PACKAGE_NAME = "com.Pinchukov.Quetz"

# Адрес проверки. На бесплатном тарифе PythonAnywhere исходящие запросы
# идут через прокси, но googleapis.com в белом списке есть.
VERIFY_URL = (
    "https://androidpublisher.googleapis.com/androidpublisher/v3/"
    "applications/{package}/purchases/products/{product}/tokens/{token}"
)

# Состояние платежа у Google: 0 — куплено, 1 — отменено, 2 — ожидает
PURCHASED = 0


def _forbidden(request):
    key = request.POST.get("secret_key") or request.GET.get("secret_key", "")
    return key != settings.API_SECRET_KEY


def _google_token():
    """Токен доступа к Play Developer API.

    Берётся из файла сервисного аккаунта, путь к нему — в настройках.
    Файла нет или библиотека не установлена — возвращаем None, и
    проверка честно отвечает, что подтвердить нечем.
    """
    path = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", "")
    if not path:
        return None

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        return None

    try:
        credentials = service_account.Credentials.from_service_account_file(
            path,
            scopes=["https://www.googleapis.com/auth/androidpublisher"],
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception:
        return None


def _ask_google(product_id, token):
    """Спрашивает у Google, настоящая ли покупка.

    Возвращает True только при явном подтверждении. Любая неясность —
    нет доступа, сеть, неожиданный ответ — это False: выдать товар по
    неподтверждённой покупке хуже, чем не выдать по настоящей, потому
    что первое повторяется бесконечно.
    """
    access_token = _google_token()
    if access_token is None:
        return None

    import urllib.error
    import urllib.parse
    import urllib.request

    # Подставляемое экранируем: настоящий токен Google состоит из
    # латиницы и цифр, но присланное клиентом может быть любым, а
    # нелатинский символ в адресе роняет запрос UnicodeEncodeError
    # ещё до отправки.
    url = VERIFY_URL.format(
        package=PACKAGE_NAME,
        product=urllib.parse.quote(product_id, safe=""),
        token=urllib.parse.quote(token, safe=""),
    )
    request = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {access_token}"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError:
        # 404 — токена нет, то есть покупка выдумана
        return False
    except Exception:
        return None

    return data.get("purchaseState") == PURCHASED


@csrf_exempt
def verify(request):
    """Проверяет покупку: POST на /purchase_verify/."""
    if _forbidden(request):
        return HttpResponseForbidden("forbidden")

    token = request.POST.get("token", "")
    product_id = request.POST.get("product_id", "")
    game_state_id = request.POST.get("game_state_id", "")

    if not token or not product_id:
        return HttpResponse(json.dumps({"error": "bad request"}), status=400)

    # Уже проверяли: отдаём прежний ответ, повторно у Google не
    # спрашиваем и вторую запись не заводим
    if Purchase.objects.filter(pk=token).exists():
        return HttpResponse(json.dumps({
            "ok": True, "valid": True, "repeat": True,
        }))

    valid = _ask_google(product_id, token)
    if valid is None:
        # Подтвердить нечем — честно говорим, что проверка недоступна,
        # а не выдаём товар на всякий случай
        return HttpResponse(json.dumps({
            "ok": False, "valid": False, "unavailable": True,
        }))

    if not valid:
        return HttpResponse(json.dumps({"ok": True, "valid": False}))

    try:
        Purchase.objects.create(
            token=token,
            game_state_id=game_state_id[:60],
            product_id=product_id[:100],
        )
    except IntegrityError:
        # Два запроса подряд с одним токеном — покупка уже записана
        pass

    return HttpResponse(json.dumps({"ok": True, "valid": True}))
