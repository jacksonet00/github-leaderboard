import threading
from . import models
from django.conf import settings


# ================================================
# Method to run task to close ended leaderboards
# ================================================


def close_ended_leaderboards():
    print('leaderboard closing task thread - Started')
    leaderboards = models.Leaderboard.objects.filter(closed=False)  # Only open leaderboards
    for leaderboard in leaderboards:
        leaderboard.close_if_ended()
    print('leaderboard closing task thread - Finished')


# ================================================
# Thread Class to close ended leaderboards
# ================================================

class LeaderboardCloseTaskThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(settings.EXECUTION_INTERVAL):
            close_ended_leaderboards()


stopFlag = threading.Event()
thread = LeaderboardCloseTaskThread(stopFlag)

if settings.AUTO_UPDATE_LEADERBOARD:
    thread.start()

# ============================================================================
# Alternate Approach
# ============================================================================
# t = threading.Timer(EXECUTION_INTERVAL, close_ended_leaderboards).start()
