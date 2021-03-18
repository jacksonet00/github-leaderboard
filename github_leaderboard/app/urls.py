from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('leaderboard/<int:id>/refresh', views.fetch_leaderboard_commits.as_view()),
]
