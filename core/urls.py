
from django.contrib import admin
from django.urls import path
import prestige.views
import quiz_word.views
import answer_counter.views
import likes.views
import state.views
import tutorial.views
import feedback.views
import metrics.views
import tournament.views
import purchase.views
import profile.views

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="root"),
    path('index/', views.index, name="index"),
    # Политика конфиденциальности: ссылку на неё требуют магазины
    path('privacy/', views.privacy, name="privacy"),
    # Время сервера: по нему считаются календарные дни наград
    path('server_time/', views.server_time, name="server_time"),

    path('save/', prestige.views.save, name="save"),
    path('prestige/', prestige.views.get_leader_board, name="get_leader_board"),
    path('prestige_clear_empty/', prestige.views.clear_all_empty, name="clear_all_empty"),

    path('save_prestige_quiz_word', quiz_word.views.save, name="save"),
    path('prestige_word_clear_empty/', quiz_word.views.clear_empty, name="clear_empty"),
    path('prestige_quiz_word/', quiz_word.views.get_leader_board, name="get_leader_board"),

    path('answer_counter_save/', answer_counter.views.save, name="answer_counter_save"),
    path('get_quest_answers_counter/', answer_counter.views.get_counter, name="get_counter"),
    path('answer_counter_clear/', answer_counter.views.clear, name="answer_counter_clear"),

    path('save_likes/', likes.views.save, name="save_likes"),
    path('get_likes/', likes.views.get_counter, name="get_likes"),
    path('likes_clear/', likes.views.clear, name="likes_clear"),

    path('metrics/', metrics.views.summary, name="metrics_summary"),

    path('state_update/', state.views.update, name="state_update"),
    path('get_best_state/', state.views.get_best_state, name="get_best_state"),
    path('state_delete/', state.views.delete, name="state_delete"),
    path('state_find/', state.views.find, name="state_find"),
    path('save_avatar/', prestige.views.save_avatar, name="save_avatar"),
    path('tutorial_step/', tutorial.views.save, name="tutorial_step"),
    path('tutorial/', tutorial.views.funnel, name="tutorial_funnel"),
    path('feedback_add/', feedback.views.add, name="feedback_add"),
    path('feedback_delete/', feedback.views.delete, name="feedback_delete"),
    path('feedback_done/', feedback.views.done, name="feedback_done"),
    path('feedback/', feedback.views.items, name="feedback_items"),

    path('tournament_status/', tournament.views.status, name="tournament_status"),
    path('tournament_join/', tournament.views.join, name="tournament_join"),
    path('tournament_score/', tournament.views.add_score, name="tournament_score"),
    path('tournament_board/', tournament.views.board, name="tournament_board"),
    path('tournament_reward/', tournament.views.reward, name="tournament_reward"),

    # Карточка игрока: её показывают рейтинг, турнир и друзья
    path('profile_save/', profile.views.save, name="profile_save"),
    path('profile_get/', profile.views.get, name="profile_get"),

    path('purchase_verify/', purchase.views.verify, name="purchase_verify"),
]
