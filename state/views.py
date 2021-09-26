import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
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

    if secret_key != "9012qw9012":
        return

    state = _get_current_state(user_id, new_name)

    prestige = state.prestige
    prestige.prestige = new_prestige
    prestige.save()

    state.name = new_name
    state.device_id = device_id
    state.state_data = new_state
    state.save()

    return HttpResponse(json.dumps({"ok": "complete save"}))


@csrf_exempt
def get_best_state(request):
    secret_key = request.POST["secret_key"]
    device_id = request.POST["device_id"]
    prestige = request.POST["prestige"]

    int_prestige = int(prestige)

    if secret_key != "9012qw9012":
        return

    state = States.objects.filter(device_id=device_id).first()
    if state and int_prestige <= state.prestige.prestige:
        return HttpResponse(json.dumps({"is_find": "true", "state": state.state_data}))

    return HttpResponse(json.dumps({"result": "Not found best state!"}))

