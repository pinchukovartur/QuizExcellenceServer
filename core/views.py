from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from prestige.models import Prestige

from django.db import models

import json


def index(request):

    return HttpResponse("ok")