import logging

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from . import methods
from . import models

User = get_user_model()
logger = logging.getLogger(__name__)

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.
def home(request):
    # logger.info('home')
    return render(request, 'pages/home.html')  # This is the same page as before but it's just a stand in


class FetchLeaderboardCommits(View):
    ''' preserve Order of application of Decorators. '''

    @method_decorator(login_required)
    # @method_decorator(decorators.admin_only) # This will only allow admins to access this method
    def get(self, request, id):
        success = methods.refresh_leaderboard_commits(id)
        if success != False:
            return JsonResponse({'success': True, 'new': success['new'], 'total': success['total']})
        else:
            return JsonResponse({'success': False})


@method_decorator(login_required, name='dispatch')
class Leaderboard(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
