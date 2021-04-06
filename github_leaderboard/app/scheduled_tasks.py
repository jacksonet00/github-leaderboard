import threading
from . import models
# ================================================
# Method to run task to close ended leaderboards
# ================================================

EXECUTION_INTERVAL = 10 # Number of seconds after which the task is executed again.

def close_ended_leaderboards():
    print('leaderboard closing task thread - Started')
    leaderboards = models.Leaderboard.objects.filter(closed=False) # Only open leaderboards
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
        while not self.stopped.wait(EXECUTION_INTERVAL):
            close_ended_leaderboards()


stopFlag = threading.Event()
thread = LeaderboardCloseTaskThread(stopFlag)

# Uncomment below line to start auto fetch thread
thread.start()


# ============================================================================
# Alternate Approach
# ============================================================================
# t = threading.Timer(EXECUTION_INTERVAL, close_ended_leaderboards).start()
