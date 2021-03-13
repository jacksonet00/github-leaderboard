import datetime
import celery

from django.contrib.auth import get_user_model
User = get_user_model()

import logging
logger = logging.getLogger(__name__)


# @celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=5)) # here we assume we want it to be run every 5 mins
@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=5)) # here we assume we want it to be run every 5 secs
def myTask():
    # Do something here
    # like accessing remote apis,
    # calculating resource intensive computational data
    # and store in cache
    # or anything you please
    print("task print", flush=True)
    logger.info('celery task')
    # print('This wasn\'t so difficult')

@celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=5)) # here we assume we want it to be run every 5 secs
def update_commit_count():
    user = ''
    token = ''
    repo_url = 'https://api.github.com/repos/jacksonet00/github-leaderboard/commits'
    # ============================================================
    
    count = methods.count_repo_commits(repo_url, user, token) # Count all commits from given repo
    u = models.User.objects.filter()

    print(count)