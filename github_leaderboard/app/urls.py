from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('leaderboard/<int:id>/refresh', views.FetchLeaderboardCommits.as_view()),
]
