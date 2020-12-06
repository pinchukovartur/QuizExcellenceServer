
from django.contrib import admin
from django.urls import path
import prestige.views
import quiz_word.views
import answer_counter.views

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name="index"),
    path('save/', prestige.views.save, name="save"),
    path('save_prestige_quiz_word', quiz_word.views.save, name="save"),
    path('prestige/', prestige.views.get_leader_board, name="get_leader_board"),
    path('prestige_clear_empty/', prestige.views.clear_all_empty, name="clear_all_empty"),
    path('prestige_word_clear_empty/', quiz_word.views.clear_empty, name="clear_empty"),
    path('prestige_quiz_word/', quiz_word.views.get_leader_board, name="get_leader_board"),
    path('answer_counter_save/', answer_counter.views.save, name="answer_counter_save"),
    path('get_quest_answers_counter/', answer_counter.views.get_counter, name="get_counter"),
]
