from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    path(
        "leaderboard/<int:id>/refresh",
        views.FetchLeaderboardCommitsView.as_view(),
        name="leaderboard_refresh",
    ),
    path(
        "leaderboard/<int:id>/close_if_ended",
        views.CloseLeaderboardIfEndedView.as_view(),
        name="close_leaderboard_if_ended",
    ),
    path("leaderboard/<int:id>", views.LeaderboardView.as_view(), name="leaderboard"),
    path(
        "leaderboard/<int:id>/manage_participants",
        views.ManageLeaderboardParticipantsView.as_view(),
        name="manage_leaderboard_participants",
    ),
    path(
        "leaderboard/<int:id>/manage_participants/delete/<int:userid>",
        views.DeleteLeaderboardParticipantsView.as_view(),
        name="delete_leaderboard_participants",
    ),
    path("dashboard", views.dashboard, name="dashboard"),
    path("delete/<int:pk>", views.leaderboard_delete, name="delete_leaderboard"),
]
