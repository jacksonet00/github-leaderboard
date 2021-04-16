from urllib.parse import urlparse

from allauth.socialaccount.models import SocialToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from github import Github

from . import models

User = get_user_model()


def refresh_leaderboard_commits(id):
    # Populates a leaderboard with commits, also works if the leaderboard is out of date
    leaderboard = get_object_or_404(models.Leaderboard, id=id)
    if leaderboard.closed:
        return False

    # Use the leaderboard's token to access github
    token = SocialToken.objects.filter(
        account__user=leaderboard.owner, account__provider="github"
    ).values_list("token")
    if token:
        token = token[0][0]
    else:
        token = ""

    repo_str = urlparse(leaderboard.repo_url).path[1:]
    if repo_str[-1] == "/":
        repo_str = repo_str[:-1]

    if token:
        repo = Github(token).get_repo(repo_str)
    else:
        repo = Github().get_repo(repo_str)

    github_commits = models.Commit.objects.filter(leaderboard=leaderboard).order_by(
        "-timestamp"
    )
    if github_commits.exists():
        latest_commit = github_commits[0]
    else:
        latest_commit = None

    github_commits = []

    # Stop adding new commits when we see the latest commit of our table in github's response
    for commit in repo.get_commits():
        if not latest_commit or commit.sha != latest_commit.nodeid:
            github_commits.append(commit)

    updated = 0
    for commit in github_commits:
        if models.Commit.objects.filter(
            nodeid=commit.sha, leaderboard=leaderboard
        ).exists():
            # This if statement might be pointless because of the latest_commit check above
            # Someone needs to test this and remove it if that is the case
            continue  # skip if commit object already exists

        # Missing author bug for some reason
        if not commit.author:
            break

        models.Commit.objects.create(
            leaderboard=leaderboard,
            user=commit.author.login,
            nodeid=commit.sha,
            message=commit.commit.message,
            url=commit.url,
            html_url=commit.html_url,
            timestamp=commit.commit.author.date,
        )
        updated += 1
    return {"total": len(github_commits), "new": updated}


def has_social_token(user):
    """Function to check if user has a social token,
    that is has a linked github account

    Returns:
        True, if they do have a github auth token on the database
        False, otherwise
    """
    token = SocialToken.objects.filter(
        account__user=user, account__provider="github"
    ).values_list("token")
    return bool(token)
