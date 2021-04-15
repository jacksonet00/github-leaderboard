import logging

import requests
from allauth.socialaccount.models import SocialToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from . import models

User = get_user_model()
_NOT_FOUND_STRING = "Not Found"  # Constant
logger = logging.getLogger(__name__)


# TODO: add more an error that says if the github link does not exist
def refresh_leaderboard_commits(id):
    # Populates a leaderboard with commits, also works if the leaderboard is out of date
    leaderboard = get_object_or_404(models.Leaderboard, id=id)
    if leaderboard.closed:
        return False

    url_str = leaderboard.repo_url.replace("https://github.com/", "").strip("/")

    user = leaderboard.owner.github_username
    token = SocialToken.objects.filter(
        account__user=leaderboard.owner, account__provider="github"
    ).values_list("token")[0][0]
    commits_url = "https://api.github.com/repos/" + url_str + "/commits"

    github_commits = models.Commit.objects.all().order_by("-timestamp")
    if github_commits.exists():
        latest_commit = github_commits[0]
    else:
        latest_commit = None

    github_commits = []
    response = None

    while commits_url:
        response = requests.get(commits_url, auth=(user, token))
        # Github pages are paginated, next url contains the next page to look at
        # If the next link doesn't exist, return null
        commits_url = response.links.get("next", {}).get("url", None)

        # If the URL isn't found, continue
        if (
            "message" in response.json()
            and response.json()["message"] == _NOT_FOUND_STRING
        ):
            logger.warning(f"GitHub API returned {_NOT_FOUND_STRING} at {commits_url}")
            continue

        # Only add commits we don't have, if you do see the latest commit, exit early
        for commit in response.json():
            if commit["node_id"] != latest_commit.nodeid and commit:
                github_commits.append(commit)
            else:
                break

    updated = 0
    if response.status_code == 200:
        for commit in github_commits:
            if models.Commit.objects.filter(nodeid=commit["node_id"]).exists():
                continue  # skip if commit object already exists

            # I am not sure why this happens but it can
            if not commit["author"]:
                return False

            models.Commit.objects.create(
                leaderboard=leaderboard,
                user=commit["author"]["login"],
                nodeid=commit["node_id"],
                message=commit["commit"]["message"],
                url=commit["url"],
                html_url=commit["html_url"],
                timestamp=commit["commit"]["author"]["date"],
            )
            updated += 1
        return {"total": len(github_commits), "new": updated}

    return False
