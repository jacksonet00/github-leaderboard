from django.shortcuts import render, get_object_or_404
import requests
import logging
from django.views import View
from django.http import JsonResponse, HttpResponse
from . import models
from . import methods
from django.contrib.auth import get_user_model
User = get_user_model()
logger = logging.getLogger(__name__)

# Create your views here.


def home(request):
    logger.info('home')
    print("task print", flush=True)
    return render(request, 'pages/home.html')  # This is the same page as before but it's just a stand in


class fetch_leaderboard_commits(View):
    def get(self, request, id):
        success = methods.refresh_leaderboard_commits(id)
        if(success != False):
            return JsonResponse({'success':True, 'new': success['new'], 'total':success['total'] })
            # return HttpResponse('successful: ' + str(success['new']) + ' out of ' + str(success['total']) + ' stored.'  )
        else:
            return JsonResponse({'success':False})
            # return HttpResponse('unable to fetch latest data')
        
class leaderboard(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        
