import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from github_leaderboard.app.forms import CreateLeaderboardForm
from github_leaderboard.app.models import Leaderboard

from . import methods, models, scheduled_tasks

if settings.AUTO_UPDATE_LEADERBOARD:
    scheduled_tasks.LEADERBOARD_UPDATE_THREAD.start()

User = get_user_model()
logger = logging.getLogger(__name__)


# Create your views here.
def home(request):
    return render(
        request, "pages/home.html"
    )  # This is the same page as before but it's just a stand in


class fetch_leaderboard_commits(View):
    """ preserve Order of application of Decorators. """

    @method_decorator(login_required)
    # @method_decorator(decorators.admin_only) # This will only allow admins to access this method
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        if leaderboard.closed:
            messages.error(self.request, "Leaderboard is closed. operation aborted.")
            return redirect("leaderboard", id=id)
        success = methods.refresh_leaderboard_commits(id)
        if success:
            # return redirect('leaderboard', kwargs={"id":id})
            msg = str(success["new"]) + " records updated"
            messages.success(self.request, msg)
            return redirect("leaderboard", id=id)
            # return JsonResponse({'success':True, 'new': success['new'], 'total':success['total'] })
        else:
            messages.error(self.request, "unexpected error occured")
            return redirect("leaderboard", id=id)
            # return JsonResponse({'success':False})


@method_decorator(login_required, name="dispatch")
class leaderboard(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)

        entries = (
            models.Commit.objects.filter(
                leaderboard=leaderboard, user__in=leaderboard.participants.all()
            )
            .values("user__github_username")
            .annotate(total=Count("user"))
            .order_by("-total")
        )

        # zero  = leaderboard.participants.filter(Count("commit_set")==0)

        users_without_commit = []
        for user in leaderboard.participants.all():
            count = user.commit_set.filter(leaderboard=leaderboard).count()
            if count == 0:
                users_without_commit.append(user)

        context = {
            "leaderboard": leaderboard,
            "entries": entries,
            "users_without_commit": users_without_commit,
            # "combined":
        }
        return render(request, "app/leaderboard.html", context)


@method_decorator(login_required, name="dispatch")
class close_leaderboard_if_ended(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        leaderboard.close_if_ended()
        return redirect("leaderboard", id=id)


@method_decorator(login_required, name="dispatch")
class manage_leaderboard_participants(View):
    def get(self, request, id):
        leaderboard = get_object_or_404(models.Leaderboard, id=id)
        context = {
            "leaderboard": leaderboard,
        }
        return render(request, "app/manage_participant.html", context)

    def post(self, request, id):
        username = request.POST["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "user does not exists")
            return redirect("manage_leaderboard_participants", id=id)

        try:
            leaderboard = get_object_or_404(models.Leaderboard, id=id)
        except models.Leaderboard.DoesNotExist:
            messages.error(request, "leaderboard does not exists")
            return redirect("manage_leaderboard_participants", id=id)

        if leaderboard.closed:
            messages.error(request, "cant add participant of closed leaderboard")
            return redirect("manage_leaderboard_participants", id=id)

        if user in leaderboard.participants.all():
            messages.error(request, "user is already a participant in this leaderboard")
            return redirect("manage_leaderboard_participants", id=id)

        leaderboard.participants.add(user)
        messages.success(request, "participant added successfully. ")
        return redirect("manage_leaderboard_participants", id=id)


@method_decorator(login_required, name="dispatch")
class delete_leaderboard_participants(View):
    def get(self, request, id, userid):
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            messages.error(request, "user does not exists")
            return redirect("manage_leaderboard_participants", id=id)

        try:
            leaderboard = get_object_or_404(models.Leaderboard, id=id)
        except models.Leaderboard.DoesNotExist:
            messages.error(request, "leaderboard does not exists")
            return redirect("manage_leaderboard_participants", id=id)
        if leaderboard.closed:
            messages.error(request, "cant remove participant of closed leaderboard")
            return redirect("manage_leaderboard_participants", id=id)

        leaderboard.participants.remove(user)
        messages.success(request, "participant removed successfully. ")
        return redirect("manage_leaderboard_participants", id=id)


def dashboard(request):
    """ View for the dashboard page of the website """
    template = "pages/dashboard.html"
    if not request.user.is_authenticated:
        return HttpResponseNotAllowed(request)
    if request.method == "GET":
        ctx = dashboard_context(request)
        return render(request, template, context=ctx)
    elif request.method == "POST":
        return dashboard_post(request)
    else:
        raise Http404("HTTP method not defined on this page")


def leaderboard_delete(request, pk=None):
    """Special view for deleting leaderboards from across the site

    kwargs:
        pk -- a leaderboard id (primary key)
    """
    template = "pages/deleteLeaderboard.html"
    if pk is not None and request.user.is_authenticated:
        leaderboard = get_object_or_404(Leaderboard, id=pk)
        if leaderboard.owner == request.user:
            ctx = {}
            success = False
            msg = ""
            if request.method == "POST":
                try:
                    leaderboard.delete()
                except Exception as e:
                    msg = f"An error occured when trying to delete {leaderboard.name}"
                    msg += "\n" + str(e)
                    ctx["message"] = msg
                    prompt = False
                else:
                    success = True
                    prompt = False
            else:
                prompt = True
            ctx = {
                "message": msg,
                "prompt": prompt,
                "success": success,
                "pk": pk,
                "ldb_name": leaderboard.name,
            }
            return render(request, template, context=ctx)
    return render(request, "403.html")


def dashboard_post(request):
    """ Handles POST for dashboard view """
    template = "pages/dashboard.html"
    form = CreateLeaderboardForm(request.POST)
    if form.is_valid():
        Leaderboard.objects.create(**form.cleaned_data, owner=request.user)
        return render(request, template, context=dashboard_context(request))
    else:
        ctx = dashboard_context(request)
        ctx["creation_form"] = form  # Send it back with error messages
        return render(request, template, context=ctx)


def dashboard_context(request):
    """Returns a context dictionary for the dashboard view
    Params:
        request - The HTTP request
    Returns:
        {
            'owned_leaderboards': dict of leaderboards owned by user
            'member_leaderboards': dict of leaderboards user is member of
            'message': message to be displayed
        }
    """
    if request.user.is_authenticated:
        owned_leaderboards = Leaderboard.objects.filter(owner=request.user)
        member_leaderboards = {}  # TODO: Need to make this possible with models
        message = f"Hello {request.user.username}"
        creation_form = CreateLeaderboardForm()
        context = {
            "owned_leaderboards": owned_leaderboards,
            "member_leaderboards": member_leaderboards,
            "message": message,
            "creation_form": creation_form,
        }
        return context
    else:
        raise PermissionDenied


def http501(message):
    """Returns a HTTP Response 501 Not Implemented
    with message as content
    """
    response = HttpResponse(message)
    response.status_code = 501
    return response
