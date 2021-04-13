from django.urls import path

from . import views

urlpatterns = [
    path("", views.home),
    path(
        "leaderboard/<int:id>/refresh",
        views.fetch_leaderboard_commits.as_view(),
        name="leaderboard_refresh",
    ),
    path(
        "leaderboard/<int:id>/close_if_ended",
        views.close_leaderboard_if_ended.as_view(),
        name="close_leaderboard_if_ended",
    ),
    path("leaderboard/<int:id>", views.leaderboard.as_view(), name="leaderboard"),
    path(
        "leaderboard/<int:id>/manage_participants",
        views.manage_leaderboard_participants.as_view(),
        name="manage_leaderboard_participants",
    ),
    path(
        "leaderboard/<int:id>/manage_participants/delete/<int:userid>",
        views.delete_leaderboard_participants.as_view(),
        name="delete_leaderboard_participants",
    ),
    path(
        "dashboard",
        views.dashboard
        name="dashboard"    
    ),
    path(
        "delete/<int:pk>",
        views.leaderboard_delete
        name="delete_leaderboard"
    ),
]
