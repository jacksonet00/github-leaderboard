from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
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
from django.db.models import Count
from django.contrib import messages


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
            # return redirect('leaderboard', kwargs={"id":id})
            msg = str(success['new']) + " records updated"
            messages.success(self.request, msg )
            return redirect('leaderboard', id=id)
            # return JsonResponse({'success':True, 'new': success['new'], 'total':success['total'] })
        else:
            messages.success(self.request, "unexpected error occured" )
            return redirect('leaderboard', id=id)
            # return JsonResponse({'success':False})

@method_decorator(login_required, name='dispatch')
class leaderboard(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        
        entries = models.Commit.objects.filter(leaderboard=leaderboard, user__in=leaderboard.participants.all()).values('user__github_username').annotate(total=Count('user')).order_by('-total')
        
        # zero  = leaderboard.participants.filter(Count("commit_set")==0)
        
        users_without_commit = []
        for user in leaderboard.participants.all():
            count = user.commit_set.filter(leaderboard=leaderboard).count()
            if(count == 0 ):
                users_without_commit.append(user)
        
        context = {
            "leaderboard":leaderboard,
            "entries":entries,
            "users_without_commit":users_without_commit,
        }
        return render(request, "app/leaderboard.html", context)

@method_decorator(login_required, name='dispatch')
class manage_leaderboard_participants(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        context = {
            "leaderboard":leaderboard,
        }
        return render(request, "app/manage_participant.html", context)
    
    def post(self, request, id):
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exists')
            return redirect('manage_leaderboard_participants', id=id)

        try:
            leaderboard = get_object_or_404(models.Leaderboard, id=id)
        except:
            messages.error(request, 'leaderboard does not exists')
            return redirect('manage_leaderboard_participants', id=id)
        
        if(user in leaderboard.participants.all()):
            messages.error(request, 'user is already a participant in this leaderboard')
            return redirect('manage_leaderboard_participants', id=id)

        leaderboard.participants.add(user)
        messages.success(request, 'participant added successfully. ')
        return redirect('manage_leaderboard_participants', id=id)


@method_decorator(login_required, name='dispatch')
class delete_leaderboard_participants(View):
    def get(self, request, id, userid):
        try:
            user = User.objects.get(id=userid)
        except:
            messages.error(request, 'user does not exists')
            return redirect('manage_leaderboard_participants', id=id)

        try:
            leaderboard = get_object_or_404(models.Leaderboard, id=id)
        except:
            messages.error(request, 'leaderboard does not exists')
            return redirect('manage_leaderboard_participants', id=id)
        
        leaderboard.participants.remove(user)
        messages.success(request, 'participant removed successfully. ')
        return redirect('manage_leaderboard_participants', id=id)
     

@method_decorator(login_required, name='dispatch')
class fetch_commits_from_all_public_repo(View):
    def get(self, request, id):
        # leaderboard = get_object_or_404(models.Leaderboard, id=id)
        return render(request, "app/fetch_commits_from_all_repo.html")
        
