from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('dashboard', views.dashboard),
    path('delete/<int:pk>', views.leaderboard_delete)
]
