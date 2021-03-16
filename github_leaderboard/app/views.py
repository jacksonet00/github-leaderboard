from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
import requests
import logging
from . import models
from . import methods
from django.contrib.auth import get_user_model
User = get_user_model()
logger = logging.getLogger(__name__)


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import decorators


# Create your views here.
def home(request):
    # logger.info('home')
    return render(request, 'pages/home.html')  # This is the same page as before but it's just a stand in

class fetch_leaderboard_commits(View):
    ''' preserve Order of application of Decorators. '''
    @method_decorator(login_required)
    # @method_decorator(decorators.admin_only) # This will only allow admins to access this method
    def get(self, request, id):
        success = methods.refresh_leaderboard_commits(id)
        if(success != False):
            return JsonResponse({'success':True, 'new': success['new'], 'total':success['total'] })
        else:
            return JsonResponse({'success':False})

@method_decorator(login_required, name='dispatch')
class leaderboard(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        
