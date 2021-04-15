from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse

USER_ROLES = (
    ("ADMIN", "ADMIN"),
    ("DEV", "DEV"),
    ("USER", "USER"),
)


class User(AbstractUser):
    """Default user for Github Leaderboard."""

    #: First and last name do not cover name patterns around the globe
    github_username = CharField(max_length=255, unique=True, blank=True, null=True)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    role = CharField(max_length=20, choices=USER_ROLES, default="ADMIN")

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
