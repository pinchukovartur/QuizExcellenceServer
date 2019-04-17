from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from quiz_word.models import QuizWordPrestige


def save(request):
    game_state_id = request.GET["game_state_id"]
    prestige = request.GET["prestige"]
    name = request.GET["name"]

    try:
        pr = QuizWordPrestige.objects.get(pk=game_state_id)
        pr.prestige = prestige
        pr.save()
    except ObjectDoesNotExist:
        QuizWordPrestige.objects.create(game_state_id=game_state_id, prestige=prestige, name=name)

    return HttpResponse("ok")
