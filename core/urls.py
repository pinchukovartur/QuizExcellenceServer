
from django.contrib import admin
from django.urls import path
from prestige import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('save/', views.save, name="save"),
    path('prestige/', views.get_leader_board, name="get_leader_board"),
]
