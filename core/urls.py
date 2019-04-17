
from django.contrib import admin
from django.urls import path
import prestige.views
import quiz_word.views

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name="index"),
    path('save/', prestige.views.save, name="save"),
    path('save_prestige_quiz_word', quiz_word.views.save, name="save"),
    path('prestige/', prestige.views.get_leader_board, name="get_leader_board"),
]
