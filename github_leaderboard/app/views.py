from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.template import loader
from django.views import View

from github_leaderboard.app.models import Leaderboard
from github_leaderboard.users.models import User

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
        return http501('POST not yet implemented')
    elif request.method == 'DELETE':
        return http501('DELETE not yet implemented')
    else:
        raise Http404('HTTP method not defined on this page')

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
    if request.user.is_authenticated:
        owned_leaderboards = Leaderboard.objects.filter(owner=request.user)
        member_leaderboards = {} # TODO: Need to make this possible with models
        message = f"Hello {request.user.name}"
    else:
        owned_leaderboards = {}
        member_leaderboards = {}
        message = "Please login!"
    context = {
        'owned_leaderboards': owned_leaderboards,
        'member_leaderboards': member_leaderboards,
        'message': message
    }
    return context

def http501(message):
    ''' Returns a HTTP Response 501 Not Implemented
        with message as content
    '''
    response = HttpResponse(message)
    response.status_code = 501
    return response