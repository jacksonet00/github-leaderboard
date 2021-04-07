from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.template import loader
from django.views import View
from django.shortcuts import get_object_or_404

from github_leaderboard.app.models import Leaderboard
from github_leaderboard.users.models import User
from github_leaderboard.app.forms import CreateLeaderboardForm

# Create your views here.
def home(request):
    return render(request, 'pages/home.html')  # This is the same page as before but it's just a stand in

def dashboard(request):
    ''' View for the dashboard page of the website '''
    template = 'pages/dashboard.html'
    if request.method == 'GET':
        ctx = dashboard_context(request)
        return render(request, template, context=ctx)
    elif request.method == 'POST':
        return dashboard_post(request)
    else:
        raise Http404('HTTP method not defined on this page')

def leaderboard_delete(request, pk=None):
    ''' Special view for deleting leaderboards from across the site 
    
        kwargs:
            pk -- a leaderboard id (primary key)
    '''
    template = 'pages/deleteLeaderboard.html'
    if pk is not None and request.user.is_authenticated:
        leaderboard = get_object_or_404(Leaderboard, id=pk)
        if leaderboard.owner == request.user:
            ctx = {}
            success = False
            msg = ''
            if request.method == "POST":
                try:
                    leaderboard.delete()
                except Exception as e:
                    msg = f'An error occured when trying to delete {leaderboard.name}'
                    msg += '\n' + str(e)
                    ctx['message'] = msg
                    prompt = False
                else:
                    success = True
                    prompt = False
            else:
                prompt = True
            ctx = {
                'message' : msg,
                'prompt': prompt,
                'success': success,
                'pk': pk,
                'ldb_name': leaderboard.name
            }
            return render(request, template, context=ctx)
    return render(request, "403.html")


def dashboard_post(request):
    ''' Handles POST for dashboard view '''
    template = 'pages/dashboard.html'
    form = CreateLeaderboardForm(request.POST)
    if form.is_valid():
        Leaderboard.objects.create(**form.cleaned_data, owner=request.user)
        return render(request, template, context=dashboard_context(request))
    else:
        ctx = dashboard_context(request)
        ctx['creation_form'] = form # Send it back with error messages
        return render(request, template, context=ctx)

def dashboard_context(request):
    ''' Returns a context dictionary for the dashboard view
        Params:
            request - The HTTP request
        Returns:
            {
                'owned_leaderboards': dict of leaderboards owned by user
                'member_leaderboards': dict of leaderboards user is member of
                'message': message to be displayed
            }
    '''
    logged_in = request.user.is_authenticated
    if logged_in:
        owned_leaderboards = Leaderboard.objects.filter(owner=request.user)
        member_leaderboards = {} # TODO: Need to make this possible with models
        message = f"Hello {request.user.name}"
        creation_form = CreateLeaderboardForm()
        context = {
            'owned_leaderboards': owned_leaderboards,
            'member_leaderboards': member_leaderboards,
            'message': message,
            'creation_form': creation_form,
            'logged_in': logged_in
        }
    else:
        context = {
            'message' : "Please login!",
            'logged_in': logged_in
        }
    return context

def http501(message):
    ''' Returns a HTTP Response 501 Not Implemented
        with message as content
    '''
    response = HttpResponse(message)
    response.status_code = 501
    return response