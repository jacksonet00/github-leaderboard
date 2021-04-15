import datetime as dt

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils import timezone

User = get_user_model()


# Create your models here.
class Result(models.Model):
    def default_score():
        return 0

    leaderboard = models.ForeignKey(
        "Leaderboard",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="results",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=default_score)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.score} points"

    def save(self, *args, **kwargs):
        if self.leaderboard:
            if self.leaderboard.closed:
                raise ValueError(
                    "Updating results of closed leaderboard is not allowed"
                )
        super().save(*args, **kwargs)


class Leaderboard(models.Model):
    def default_start_datetime():
        return timezone.now()

    def default_end_datetime():
        return timezone.now() + dt.timedelta(days=7)

    name = models.CharField(max_length=255)
    start = models.DateTimeField(default=default_start_datetime)
    end = models.DateTimeField(default=default_end_datetime)
    repo_url = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField(
        User, blank=True, related_name="leaderboards_participated"
    )
    closed = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Leaderboard, self).__init__(*args, **kwargs)
        self.initial_closed = self.closed  # remember initial value

    def get_ranked_user_commit_data(self):
        # From the Commit table, filter out by the github_user of the participants, and return a count of the commits

        # Yes this is ugly don't @ me
        # Get the usernames of participants as a set
        user_set = set(
            entity[0]
            for entity in self.participants.all().values_list("github_username")
        )

        # Only works for users with at least one commit
        ranked_data = list(
            Commit.objects.filter(leaderboard=self, user__in=user_set)
            .values("user")
            .annotate(total=Count("user"))
            .order_by("-total")
        )

        # users who dont have any commit
        for user in user_set.difference(set(entity["user"] for entity in ranked_data)):
            ranked_data.append({"user": user, "total": 0})

        return ranked_data

    def close_if_ended(self):
        if not self.closed:
            today = timezone.now()
            if today > self.end:
                print("Closing leaderboard " + str(self.name))
                self.refresh()  # fetch latest commit data from repo before closing
                ranked_data, users_without_commit = self.get_ranked_user_commit_data()
                for entry in ranked_data:
                    user = User.objects.get(
                        github_username=entry["user__github_username"]
                    )
                    Result.objects.create(
                        leaderboard=self, user=user, score=entry["total"]
                    )

                for user in users_without_commit:
                    Result.objects.create(leaderboard=self, user=user, score=0)

                self.closed = True
                self.save()
                print("leaderboard " + str(self.name) + " closed successfully.")
        # else:
        #     raise ValueError("closing of already closed leaderboard is not allowed")

    def __str__(self):
        return self.name


class Commit(models.Model):
    leaderboard = models.ForeignKey(
        "Leaderboard", on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.CharField(max_length=255, null=True)
    nodeid = models.CharField(max_length=255)
    message = models.TextField()
    url = models.URLField()
    html_url = models.URLField()
    timestamp = models.DateTimeField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}: {self.timestamp} - {self.message} commits"

    def save(self, *args, **kwargs):
        if self.leaderboard:
            if self.leaderboard.closed:
                raise ValueError(
                    "Updating commits of closed leaderboard is not allowed"
                )
        super().save(*args, **kwargs)
